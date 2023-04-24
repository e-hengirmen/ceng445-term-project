import json
from User import User
import random
from enum import Enum
from queue import Queue


def roll_a_dice():
    return random.randint(1, 6)


def take_chance_card():
    return random.randint(0, 8)


class Board:

    def __init__(self, file,number_of_users=4):
        data = json.loads(file.read())
        self.number_of_users=number_of_users

        # file variables
        self.cells = data["cells"]  # used as map to play the game
        self.N = len(data["cells"])  # number of cells

        # costs or prizes
        self.upgrade = data["upgrade"]
        self.teleport = data["teleport"]
        self.jailbail = data["jailbail"]
        self.tax = data["tax"]
        self.lottery = data["lottery"]
        self.startup = data["startup"]
        self.lapping_salary = data["lapping_salary"]

        # self.chance_card_list=data["chances"]   #used as chance card list which it is

        self.chance_card_list = Queue()
        for card in data["chances"]:
            self.chance_card_list.put(card["type"])

        # property user containers
        self.properties = []
        self.user_dict = {}
        self.color_list = []
        self.get_properties()

        # state variables
        self.unready_count = 0
        self.WaitingState = True
        self.active_user_state = TURN_STATE.turn_start

        # order variables
        self.order = []
        self.active_user_index = 0

        # properties group by color
        self.properties_by_color = {}
        self.get_colors()

        self.callback = {}

    def get_colors(self):
        """
            Groups properties by their color,
            This color groups were added to be used in color_upgrade and downgrade
        """
        for color in self.color_list:
            self.properties_by_color[color] = []
        for prop in self.properties:
            self.properties_by_color[prop.color].append(prop)


    def get_properties(self):
        """
            Manages property ownership and color sets.
            get_properties is used to create property objects from cells
            this way the properties can be bought and be associated to the user later on
        """
        for cell in self.cells:
            if cell['type'] == 'property':
                current_property = Property(cell)
                cell['property'] = current_property
                self.properties.append(current_property)
                if cell['color'] not in self.color_list:
                    self.color_list.append(cell['color'])

    def attach(self, user, callback, turncb):  # controlled
        """
            creates a user dictionary(accessed by user object also adds user to the current game)
            Manages player participation in the game.
            order of play is depended on the order of connection
        """
        if(self.unready_count==self.number_of_users):       # for first attaching then starting readies
            return



        if (self.WaitingState == False):
            return
        if user in self.user_dict.keys():
            return
        self.user_dict[user] = {"user": user,
                                "money": self.startup,
                                "position": 0,
                                "properties": [],
                                "ready": False,
                                "guilty": False,
                                "jailFree": 0,
                                "callback": callback,
                                "turncb": turncb}
        self.unready_count += 1
        self.order.append(user)

    def detach(self, user):  # controlled
        """
            Handles players leaving the game.
            Removes a user from the game by removing them from the player order and resetting the ownership of their properties

            called when the user is bankrupt

            only call for a user on their turn
        """
        #
        if user in self.user_dict:
            self.order.remove(user)
            for prop in self.user_dict[user]["properties"]:
                prop.owner = None
            del self.user_dict[user]
            # self.next_user()
            n = len(self.order)
            self.active_user_index = (self.active_user_index) % n
            self.active_user_state = TURN_STATE.turn_start
            if (n == 1):
                self.CALL_THEM_BACK(f"Game has ended - {self.order[0]} wins!!!")

    def ready(self, user):  # controlled
        """
            Marks a user as ready and starts the game if all users are ready and there are at least two players.
            This is necessary for synchronizing player readiness before starting the game.
        """
        if(self.WaitingState==False):
            return
        if self.user_dict[user]["ready"] == False:
            self.user_dict[user]["ready"] = True
            self.unready_count -= 1
            if (self.unready_count == 0 and len(self.user_dict) >= 2):
                self.initiate_game(user)

    def initiate_game(self,me):  # since there might be more things we need to add
        """
            Transitioning from the waiting state to the active game state.
        """
        self.WaitingState = False
        for user in self.order:
            if user!=me:
                user.mutex.release()
        self.CALL_THEM_BACK(self.get_report(self.order[0]))

    # for exception handling real turn function is below called: turn_helper
    def turn(self, user):
        """
            for exception handling real turn function is below called: turn_helper
        """
        command = self.TURN_TO_USER(user)
        try:
            return self.turn_helper(user, command)
        except MonopolyException as e:
            self.CALL_THEM_BACK(f"ERROR: {e}\n",user)
            return user

    def turn_helper(self, user, command):
        """
            Processes a user's command during their turn, based on the current state of the game and the user's turn.

            Jail case: If the user is in jail and tries to roll doubles to get out, roll the dice, and check the result.
            If they roll doubles, set the user as not guilty
            If the user wants to bail out of jail, decrease their jail-free cards or money, set the user as not guilty
            If the user tries any other command, raise an exception informing them that they should either roll or bail.
            Move on to the next user.

            Normal roll case:
                If the user rolls the dice, calculate their new position, update their money if they pass the start, and execute the cell's action.

            Buy case: If the user wants to buy a property, check if they can buy it.
            If they meet the conditions, decrease their money, add the property to their ownership, and set them as the owner of the property.
            Move on to the next user.

            Upgrade case:
                If the user wants to upgrade a property, check if they can upgrade it
                (they have rolled, the cell is a property, they own it, it's not at the max level, and they have enough money).
                If they meet the conditions, update their money and upgrade the property.
                Move on to the next user.

            Teleport case:
                If the user wants to teleport, check if they can teleport (they are in the teleport state and the target cell is a property).
                If they meet the conditions, update their position and execute the cell's action based on property ownership.

            End turn case:
                If the user wants to end their turn, check if they can end it (they have rolled or teleported).
                If they meet the conditions, move on to the next user.

            Invalid command case:
                If the user enters an invalid command, raise an exception informing them about the invalid command.

            Bankruptcy case:
                If the user has negative money, remove them from the game.

            Call the user's callback with their updated game report and return the active user's username.
        """
        if self.WaitingState == True:
            raise WaitingForReadyException("Not everyone is ready")
        if self.order[self.active_user_index] != user:
            raise NotYourTurnException("It is " + self.order[self.active_user_index].username + "'s turn")
        # jail case
        # The user will either roll or bail
        # when bailing the get out of jail free card will always be used if user has any
        if self.user_dict[user]["guilty"] == True:
            if command == "Roll":
                dice1 = roll_a_dice()
                dice2 = roll_a_dice()
                # show_dice_roll(dice1,dice2)
                self.CALL_THEM_BACK(f"{user.username} rolled {dice1} {dice2}")
                if (dice1 == dice2):
                    self.user_dict[user]["guilty"] = False
                    self.CALL_THEM_BACK(f"{user.username} is now out of jail")

            # Below 2 cases were only added for testing TODO delete later
            elif command == "DoubleDice":
                # show_dice_roll(dice1,dice2)
                self.CALL_THEM_BACK(f"{user.username} rolled 6 6")
                self.user_dict[user]["guilty"] = False
                self.CALL_THEM_BACK(f"{user.username} is now out of jail")
            elif command == "NotDoubleDice":
                # show_dice_roll(dice1,dice2)
                self.CALL_THEM_BACK(user, f"{user.username} rolled 3 5")

            elif command == "Bail":
                if self.user_dict[user]["jailFree"] > 0:
                    self.user_dict[user]["jailFree"] -= 1
                    self.chance_card_list.put("jail_free")
                else:
                    self.user_dict[user]["money"] -= self.jailbail
                self.user_dict[user]["guilty"] = False
                self.CALL_THEM_BACK(f"{user.username} is now out of jail")
            else:
                raise WrongCommandException(
                    f"you're in jail, your command was \"{command}\" it should either be Roll or Bail")
            self.next_user()

        # normal Roll
        elif command == "Roll":  # controlled
            """
            u can roll:
                if u haven't rolled this turn
            """
            if self.active_user_state != TURN_STATE.turn_start:
                raise WrongStateException("Already rolled")
            dice1 = roll_a_dice()
            dice2 = roll_a_dice()
            # show_dice_roll(dice1,dice2)
            roll_res = dice1 + dice2
            self.CALL_THEM_BACK(f"rolled {dice1} {dice2}")

            # below 3 lines calculate your new position after roll and adds lapping salary if u have passed the starting line
            self.user_dict[user]["position"] = (self.user_dict[user]["position"] + roll_res)
            self.user_dict[user]["money"] += self.lapping_salary * (self.user_dict[user]["position"] // self.N)
            self.user_dict[user]["position"] %= self.N
            # self.execute_cell(self.user_dict[user]["position"])
            self.execute_cell(self.user_dict[user], self.cells[self.user_dict[user]["position"]])

        # Roll given number for testing purposes only TODO DELETE LATER
        elif command.startswith("Roll("):
            """
            u can roll:
                if u haven't rolled this turn
            """
            if self.active_user_state != TURN_STATE.turn_start:
                raise WrongStateException("Already rolled")
            roll_res = int(command[5:-1])
            self.CALL_THEM_BACK(f"rolled {roll_res}")

            # below 3 lines calculate your new position after roll and adds lapping salary if u have passed the starting line
            self.user_dict[user]["position"] = (self.user_dict[user]["position"] + roll_res)
            self.user_dict[user]["money"] += self.lapping_salary * (self.user_dict[user]["position"] // self.N)
            self.user_dict[user]["position"] %= self.N
            # self.execute_cell(self.user_dict[user]["position"])
            self.execute_cell(self.user_dict[user], self.cells[self.user_dict[user]["position"]])
        elif command == "Buy":  # controlled
            """
            you can buy it if:
                u have rolled 
                the place u are on is a property
                Nobody owns it
                u have money
            """
            if self.active_user_state != TURN_STATE.buy_wait:
                raise WrongStateException("You cannot buy if you are teleporting or have not rolled")
            if self.cells[self.user_dict[user]["position"]]["type"] != "property":
                raise NotPropertyException("Not a property")

            # getting user dicitionary(since user's current game data is stored within here)
            current_user_dict = self.user_dict[user]
            position = current_user_dict["position"]
            current_property = self.cells[position]["property"]

            if current_property.owner != None:
                raise AlreadyOwnedException("property owned by " + current_property.owner.username)
            if current_property.price > current_user_dict["money"]:
                raise UPoorException("Not enough money")

            # paying for and buying property
            current_user_dict["money"] -= current_property.price
            current_user_dict["properties"].append(current_property)
            current_property.owner = user

            self.next_user()
        elif command == "Upgrade":  # controlled
            """
            you can upgrade it if:
                u have rolled 
                the place u are on is a property
                u own it
                its not at max level
                u have money
            """
            if self.active_user_state != TURN_STATE.buy_wait:
                raise WrongStateException("You cannot upgrade if you are teleporting or have not rolled")
            if self.cells[self.user_dict[user]["position"]]["type"] != "property":
                raise NotPropertyException("This cell is not a property")

            # getting user dicitionary(since user's current game data is stored within here)
            current_user_dict = self.user_dict[user]
            position = current_user_dict["position"]
            current_property = self.cells[position]["property"]

            if current_property.owner != user:
                raise NotOwnedException("This property does not belong to you")
            if current_property.at_max_level():
                raise MaxLevelException("Already at max level")
            if self.upgrade > current_user_dict["money"]:
                raise UPoorException("Not enough Money")

            # paying for the upgrade and upgrading the property
            current_user_dict["money"] -= self.upgrade
            current_property.upgrade()

            self.next_user()
        elif command.startswith("Teleport"):  # controlled       #"Teleport(Newcell)":
            """
            teleport if:
                U are on teleport or u have taken teleport card
                the place u are teleporting must be a property
            """
            if self.active_user_state != TURN_STATE.teleport_wait:
                raise WrongStateException("Not in teleport state")
            if not command[9:-1].isnumeric():
                raise NotPropertyException("Can only teleport to properties with given indexes")

            # gets teleport cell index
            next_cell_index = int(command[9:-1])
            next_cell_index -= 1
            if len(self.cells) <= next_cell_index or next_cell_index < 0:
                raise OutOfRangeException(
                    f"give the index of the property you want to teleport\n You gave {next_cell_index + 1} it should be in the range [1,{len(self.cells)}]")
            if self.cells[next_cell_index]["type"] != "property":
                raise NotPropertyException("Can only teleport to properties")

            # teleports to cell
            self.user_dict[user]["position"] = next_cell_index

            # either pays if bought or goes to buy or upgrade if ownerless or owned by user
            current_property = self.cells[next_cell_index]["property"]
            if current_property.owner == None or current_property.owner == user:
                self.active_user_state = TURN_STATE.buy_wait
            elif current_property.owner != user:
                current_property.pay_current_rent(self.user_dict[user], self.user_dict[current_property.owner])
                self.next_user()
        elif command == "EndTurn":  # controlled
            # end turn if rolled
            if self.active_user_state != TURN_STATE.buy_wait:
                raise WrongStateException("Can not end turn if roll or teleport is needed")
            self.next_user()
        else:
            raise WrongCommandException("Your command: \"" + command + "\" is not valid")

        # Goes bankrupt if no money is left
        if self.user_dict[user]["money"] < 0:  # controlled
            self.detach(user)
            return None

        self.CALL_THEM_BACK(self.get_report(user))

        return self.order[self.active_user_index]

    def execute_cell(self, current_user_dict, cell):  # controlled
        """
            This function handles the user interaction with the cell they land on after a dice roll or teleport.
            It defines the consequences based on the cell type and updates the user's status accordingly.

            - start: If the cell type is "start", the function proceeds to the next user's turn.
            - jail: If the cell type is "jail", the function proceeds to the next user's turn.
            - tax: If the cell type is "tax", the user's money is decreased by the tax amount multiplied by the number of properties they own.
            - gotojail: If the cell type is "gotojail", the user is moved to the nearest jail cell, and their "guilty" status is set to True.
            - teleport: If the cell type is "teleport", the user's money is decreased by the teleport cost, and the user's state is set to "teleport_wait".
            - property: If the cell type is "property", the function checks if the property is unowned or if it is owned by the current user or another user. If unowned, the user's state is set to "buy_wait". If owned by another user, the current user pays rent to the property owner.
            - chance: If the cell type is "chance", the function retrieves a chance card and applies the card's effect. The effects vary depending on the card (e.g., upgrade, downgrade, gotojail, jail_free, teleport, lottery, tax).
        """
        if cell["type"] == "start":  # controlled
            self.next_user()
        elif cell["type"] == "jail":  # controlled
            self.next_user()
        elif cell["type"] == "tax":  # controlled
            current_user_dict["money"] -= self.tax * len(current_user_dict["properties"])
            self.next_user()
        elif cell["type"] == "gotojail":  # controlled
            self.CALL_THEM_BACK(f"{current_user_dict['user'].username} was sent to prison")
            # find nearest jail cell then go(it goes on your record ) )
            mypos = current_user_dict["position"]

            # We are finding the nearest cell from left and right and choosing the nearest one
            for addition in range(self.N):
                if self.cells[(mypos + addition) % self.N]["type"] == "jail":
                    j_hi = addition
                    break
            for addition in range(self.N):
                if self.cells[(mypos - addition + self.N) % self.N]["type"] == "jail":
                    j_lo = addition
                    break
            if j_hi < j_lo:
                jail_pos = (mypos + j_hi) % self.N
            else:
                jail_pos = (mypos - j_lo + self.N) % self.N
            current_user_dict["position"] = jail_pos
            current_user_dict["guilty"] = True
            self.next_user()
        elif cell["type"] == "teleport":  # controlled
            # implementation at turn
            current_user_dict["money"] -= self.teleport

            self.active_user_state = TURN_STATE.teleport_wait
        elif cell["type"] == "property":  # controlled
            current_property = cell["property"]
            if current_property.owner == None:
                self.active_user_state = TURN_STATE.buy_wait
            elif current_property.owner != current_user_dict["user"]:
                current_property.pay_current_rent(current_user_dict, self.user_dict[current_property.owner])
                self.next_user()
            else:  # if user owns it
                self.active_user_state = TURN_STATE.buy_wait
        elif cell["type"] == "chance":
            # First getting the top chance card from the card list
            card = self.chance_card_list.get()
            NEXT_USER_FLAG = True
            PUT_CARD_BACK_FLAG = True

            # informing users of the card
            self.CALL_THEM_BACK(f"{current_user_dict['user'].username} landed on a chance card {card}")

            if card == 'upgrade' or card == 'downgrade':  # controlled
                """selected_cell = int(input('select a cell to upgrade'))
                self.turn(current_user_dict['user'], f'Pick{selected_cell}-{card_number}')"""
                owns_property = len(current_user_dict["properties"])
                # Can only be used when user has properties
                while owns_property:
                    response_string = current_user_dict["turncb"]('select a cell you own to' + card + '(in the form Pick(cell number)):')
                    if not (response_string.startswith("Pick(") and
                            response_string.endswith(")") and
                            response_string[5:-1].isnumeric()):
                        continue
                    cell_index = int(response_string[5:-1])
                    cell_index -= 1
                    if self.cells[cell_index]["type"] != "property":
                        continue

                    # upgrading or downgrading the propert if the user owns it
                    current_property = self.cells[cell_index]["property"]
                    if current_property.owner != current_user_dict["user"]:
                        continue
                    if card == 'upgrade':
                        current_property.upgrade()
                    elif card == 'downgrade':
                        current_property.downgrade()
                    break

            elif card == 'color_upgrade' or card == 'color_downgrade':  # controlled
                owns_property = len(current_user_dict["properties"])
                # Can only be used when user has properties
                while owns_property:
                    selected_color = current_user_dict["turncb"]('select a color to ' + card[6:] + ' that you have at least one property:')
                    # looking if the user has that color type property
                    if selected_color not in self.color_list:
                        continue
                    flag = False
                    for prop in self.properties_by_color[selected_color]:
                        if prop.owner == current_user_dict["user"]:
                            flag = True
                            break
                    if flag == False:
                        continue

                    # doing the upgrade or downgrade
                    for prop in self.properties_by_color[selected_color]:
                        if card == 'color_upgrade':
                            prop.upgrade()
                        if card == 'color_downgrade':
                            prop.downgrade()
                    break

            elif card == 'gotojail':  # controlled
                self.CALL_THEM_BACK(f"{current_user_dict['user'].username} was sent to prison")
                mypos = current_user_dict["position"]

                # Finding the nearest jail cell by comparing left nearest and right nearest
                for addition in range(self.N):
                    if self.cells[(mypos + addition) % self.N]["type"] == "jail":
                        j_hi = addition
                        break
                for addition in range(self.N):
                    if self.cells[(mypos - addition + self.N) % self.N]["type"] == "jail":
                        j_lo = addition
                        break
                if j_hi < j_lo:
                    jail_pos = (mypos + j_hi) % self.N
                else:
                    jail_pos = (mypos - j_lo + self.N) % self.N
                current_user_dict["position"] = jail_pos
                current_user_dict["guilty"] = True

            elif card == 'jail_free':  # controlled
                current_user_dict['jailFree'] += 1
                PUT_CARD_BACK_FLAG = False

            elif card == 'teleport':  # controlled
                """selected_cell = int(input('select a cell to teleport'))
                self.turn(current_user_dict['user'], f'Teleport{selected_cell}')"""
                self.active_user_state = TURN_STATE.teleport_wait
                NEXT_USER_FLAG = False

            elif card == 'lottery':  # controlled
                current_user_dict['money'] += self.lottery
            elif card == 'tax':  # controlled
                current_user_dict["money"] -= self.tax * len(current_user_dict["properties"])

            # if the turn should end NEXT_USER_FLAG will be True(it is default True)
            # if the card should be put back to the list PUT_CARD_BACK_FLAG will be True(it is default True)
                # only false for get out of jail free
            if (NEXT_USER_FLAG):
                self.next_user()
            if (PUT_CARD_BACK_FLAG):
                self.chance_card_list.put(card)

    def getuserstate(self, user):  # controlled
        # print({k.username: {'money': v['money'], 'properties': [str(prop) for prop in v['properties']]} for k, v in self.user_dict.items()})
        str_list = []
        for k, v in self.user_dict.items():
            str_list.append(str({k.username: {'money': v['money'], "position": 1 + v["position"]}}))
            for prop in v['properties']:
                str_list.append("\t" + prop.user_visualization())
        return "\n".join(str_list)

    def getboardstate(self):  # controlled
        return "\n".join(list(map(str, self.cells)))
        """for property in self.properties:
            print(property)"""

    def get_report(self, user):
        """
            This function generates a report, combining the board state, current user state, last play, and turn details.
            It returns a string so that whe can use it on callback function
        """
        bs = self.getboardstate()
        us = self.getuserstate(user)

        lp = ("LAST PLAY:\t{:<{uL}} position: {:<{pL}} cell: {}".format(
            user.username,
            self.user_dict[user]["position"] + 1,
            self.cells[self.user_dict[user]["position"]],
            uL=20,
            pL=3
        ))
        to = ("TURN ON:\t{:<{uL}} position: {:<{pL}} cell: {:<{cL}}".format(
            self.order[self.active_user_index].username,
            self.user_dict[self.order[self.active_user_index]]["position"] + 1,
            str(self.cells[self.user_dict[self.order[self.active_user_index]]["position"]]),
            uL=20,
            pL=3,
            cL=20
        ))
        return bs + "\n" + "\n" + us + "\n" + "\n" + lp + "\n" + to + "\n" + "\n"\
            +"---------------------------------------------------------------------------------------------\n\n"

    def ListCommands(self, user):
        """
            Returns avaliable command list for the user
            It returns a string so that whe can use it on turncb function
        """
        str_list = [user.username]
        if self.user_dict[user]["guilty"]:
            str_list.append("You are at jail")
            str_list.append("You have " + str(self.user_dict[user]["jailFree"]) + " jailFree cards")
            str_list.append("Avaliable commands to you are:")
            str_list.append("\tRoll")
            str_list.append("\tBail")
        elif self.active_user_state == TURN_STATE.turn_start:
            str_list.append("You are at start of the turn")
            str_list.append("Avaliable commands to you are:")
            str_list.append("\tRoll")
        elif self.active_user_state == TURN_STATE.teleport_wait:
            str_list.append("You are in teleportation state")
            str_list.append("Avaliable commands to you are:")
            str_list.append("\tTeleport(index)")
        elif self.active_user_state == TURN_STATE.buy_wait:
            str_list.append("You are in last state")
            str_list.append("Avaliable commands to you are:")
            str_list.append("\tEndTurn")
            if (self.cells[self.user_dict[user]["position"]]["property"].owner == None):
                str_list.append("\tBuy")
            else:
                str_list.append("\tUpgrade")
        return "\n".join(str_list)

    def CALL_THEM_BACK(self,message,last_played_user=None):  # TODO change comments with uncommented also remove last played user
         if(last_played_user==None):
             for current_user_dict in self.user_dict.values():
                current_user_dict["callback"](message)
         else:
             self.user_dict[last_played_user]["callback"](message)

    def TURN_TO_USER(self, user):
        """
            gets command from the current user
        """
        command = self.user_dict[user]["turncb"](self.ListCommands(user))
        return command

    # ends turn
    def next_user(self):  # controlled
        """
            Ends Turn and starts next user's turn
        """
        n = len(self.order)
        self.active_user_index = (self.active_user_index + 1) % n
        self.active_user_state = TURN_STATE.turn_start


class Property:
    max_level = 5

    def __init__(self, prop_dict):
        self.name = prop_dict["name"]
        self.cell = prop_dict["cell"]
        self.color = prop_dict["color"]
        self.price = prop_dict["price"]
        self.rents = prop_dict["rents"]

        self.owner = None
        self.level = 1

    def __str__(self):
        return str({
            "name": self.name,
            "cell": self.cell,
            "color": self.color,
            "price": self.price,
            "rents": self.rents,
            "owner": self.owner.username if self.owner != None else None,
            "level": self.level,
        })

    def user_visualization(self):
        """
             Added so a property can be visualized inside a list of properties
        """
        return str({
            "name": self.name,
            "current rent": self.get_current_rent(),
            "level": self.level,
            "cell": self.cell,
            "color": self.color,
        })

    def get_current_rent(self):
        return self.rents[self.level - 1]

    def pay_current_rent(self, renter_user_dict, owner_user_dict):
        if (owner_user_dict["guilty"] == False):
            renter_user_dict["money"] -= self.rents[self.level - 1]
            owner_user_dict["money"] += self.rents[self.level - 1]

    def at_max_level(self):
        return (self.level >= self.max_level)

    def at_min_level(self):
        return (self.level == 1)

    """def __repr__(self):             #TODO using like this might create problems
        return self.__str__()"""

    def upgrade(self):
        if self.level < self.max_level:
            self.level += 1

    def downgrade(self):
        if self.level > 1:
            self.level -= 1


class MonopolyException(Exception):
    pass


class NotOwnedException(MonopolyException):
    pass


class AlreadyOwnedException(MonopolyException):
    pass


class NotPropertyException(MonopolyException):
    pass


class UPoorException(MonopolyException):
    pass


class WrongStateException(MonopolyException):
    pass


class WaitingForReadyException(MonopolyException):
    pass


class NotYourTurnException(MonopolyException):
    pass


class MaxLevelException(MonopolyException):
    pass


class WrongColorException(MonopolyException):
    pass


class WrongCommandException(MonopolyException):
    pass


class OutOfRangeException(MonopolyException):
    pass


class TURN_STATE(Enum):
    turn_start = 1
    teleport_wait = 2
    buy_wait = 3

# raise UPoorException()
