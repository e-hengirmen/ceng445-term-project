import json
from User import User
import random
from enum import Enum
from queue import Queue



def roll_a_dice():
    return random.randint(1, 6)
def take_chance_card():
    return random.randint(0,8)

class Board:

    def __init__(self,file):
        data=json.loads(file.read())

        # file variables
        self.cells=data["cells"]            #used as map to play the game
        self.N=len(data["cells"])
        self.upgrade = data["upgrade"]
        self.teleport = data["teleport"]
        self.jailbail = data["jailbail"]
        self.tax = data["tax"]
        self.lottery = data["lottery"]
        self.startup = data["startup"]
        #self.chance_card_list=data["chances"]   #used as chance card list which it is

        self.chance_card_list=Queue()
        for card in data["chances"]:
            self.chance_card_list.put(card["type"])



        # property user containers
        self.properties=[]
        self.user_dict={}
        self.color_list=[]
        self.get_properties()

        # state variables
        self.unready_count=0
        self.WaitingState=True
        self.active_user_state=TURN_STATE.turn_start

        # order variables
        self.order=[]
        self.active_user_index=0

        # TODO  non-given
        self.lapping_salary=500

        # properties group by color
        self.properties_by_color = {}
        self.get_colors()

    def get_colors(self):
        for color in self.color_list:
            self.properties_by_color[color] = []
        for prop in self.properties:
            self.properties_by_color[prop.color].append(prop)

    def get_properties(self):
        for cell in self.cells:
            if cell['type']=='property':
                current_property=Property(cell)
                cell['property']=current_property
                self.properties.append(current_property)
                if cell['color'] not in self.color_list:
                    self.color_list.append(cell['color'])

    def attach(self, user, callback,turncb):    # controlled
        self.user_dict[user]={"user":user,
                              "money":self.startup,
                              "position":0,
                              "properties":[],
                              "ready":False,
                              "guilty":False,
                              "jailFree":0,}
        self.unready_count+=1
        self.order.append(user)
        # TODO whatever callback is
    def detach(self, user):             # controlled
        #only call for a user on their turn
        if user in self.user_dict:
            del self.user_dict[user]
            self.order.remove(user)
            for prop in self.user_dict[user]["properties"]:
                prop.owner=None
            # self.next_user()
            n = len(self.order)
            self.active_user_index = (self.active_user_index) % n
            self.active_user_state = TURN_STATE.turn_start
            if(n==1):
                print("Game has ended - {} wins!!!".format(self.order[0]))
    def ready(self, user):              # controlled
        if self.user_dict[user]["ready"]==False:
            self.user_dict[user]["ready"]=True
            self.unready_count-=1
            if (self.unready_count==0 and len(self.user_dict)>=2):
                self.initiate_game()
    def initiate_game(self):    #since there might be more things we need to add
        self.WaitingState=False

    def turn(self, user, command):
        try:
            return self.turn_helper(user,command)
        except MonopolyException as e:
            print("ERROR:", e)
            return user

    def turn_helper(self, user, command):
        if self.WaitingState==True:
            raise WaitingForReadyException("Not everyone is ready")
        if self.order[self.active_user_index]!=user:
            print("The turn belongs to",user.username)
            raise NotYourTurnException("It is "+self.order[self.active_user_index]+"'s turn")
        # jail case
        if self.user_dict[user]["guilty"]==True:
            if command == "Roll":
                dice1 = roll_a_dice()
                dice2 = roll_a_dice()
                # show_dice_roll(dice1,dice2)
                if(dice1==dice2):
                    self.user_dict[user]["guilty"]=False
            elif command == "Bail":
                if self.user_dict[user]["jailFree"] >= 0:
                    self.user_dict[user]["jailFree"] -= 1
                    self.chance_card_list.put("jail_free")
                else:
                    self.user_dict[user]["money"] -= self.jailbail
                self.user_dict[user]["guilty"] = False
            else:
                raise WrongCommandException("you're in jail, your command was \{{}\} it should either be Roll or Bail".format(command))
            self.next_user()

        #normal roll
        elif command == "Roll":     # controlled
            '''
            u can roll:
                if u haven't rolled this turn
            '''
            if self.active_user_state!=TURN_STATE.turn_start:
                raise WrongStateException("Already rolled")
            dice1=roll_a_dice()
            dice2=roll_a_dice()
            #show_dice_roll(dice1,dice2)
            roll_res=dice1+dice2
            print("rolled",roll_res)
            self.user_dict[user]["position"]=(self.user_dict[user]["position"]+roll_res)
            self.user_dict[user]["money"]+=self.lapping_salary*(self.user_dict[user]["position"]//self.N)
            self.user_dict[user]["position"]%=self.N
            #self.execute_cell(self.user_dict[user]["position"])
            self.execute_cell(self.user_dict[user],self.cells[self.user_dict[user]["position"]])
        elif command == "Buy":      # controlled
            '''
            you can buy it if:
                u have rolled 
                the place u are on is a property
                Nobody owns it
                u have money
            '''
            if self.active_user_state!=TURN_STATE.buy_wait:
                raise WrongStateException("You cannot buy if you are teleporting or have not rolled")
            if self.cells[self.user_dict[user]["position"]]["type"]!="property":
                raise NotPropertyException("Not a property")

            current_user_dict = self.user_dict[user]
            position=current_user_dict["position"]
            current_property = self.cells[position]["property"]

            if current_property.owner != None:
                raise AlreadyOwnedException("property owned by "+current_property.owner.username)
            if current_property.price>current_user_dict["money"]:
                raise UPoorException("Not enough money")



            current_user_dict["money"]-=current_property.price
            current_user_dict["properties"].append(current_property)
            current_property.owner=user

            self.next_user()
        elif command == "Upgrade":      # controlled
            '''
            you can upgrade it if:
                u have rolled 
                the place u are on is a property
                u own it
                its not at max level
                u have money
            '''
            if self.active_user_state!=TURN_STATE.buy_wait:
                raise WrongStateException("You cannot upgrade if you are teleporting or have not rolled")
            if self.cells[self.user_dict[user]["position"]]["type"] != "property":
                raise NotPropertyException("This cell is not a property")
            current_user_dict = self.user_dict[user]
            position = current_user_dict["position"]
            current_property = self.cells[position]["property"]
            if current_property.owner!=user:
                raise NotOwnedException("This property does not belong to you")
            if current_property.at_max_level():
                raise MaxLevelException("Already at max level")
            if self.upgrade>current_user_dict["money"]:
                raise UPoorException("Not enough Money")
            current_user_dict["money"] -= self.upgrade
            current_property.upgrade()
            self.next_user()
        elif command.startswith("Teleport"):     # controlled       #"Teleport(Newcell)":
            '''
            teleport if:
                U are on teleport or u have taken teleport card
                the place u are teleporting is a property
            '''
            if self.active_user_state!=TURN_STATE.teleport_wait:
                raise WrongStateException("Not in teleport state")
            next_cell_index = int(command[9:-1])
            if self.cells[next_cell_index]["type"]!="property":
                raise NotPropertyException("Can only teleport to properties")

            self.user_dict[user]["position"] = next_cell_index

            current_property = self.cells[next_cell_index]["property"]
            if current_property.owner == None or current_property.owner == user:
                self.active_user_state = TURN_STATE.buy_wait
            elif current_property.owner != user:
                current_property.pay_current_rent(self.user_dict[user],self.user_dict[current_property.owner])
                self.next_user()
        elif command == "EndTurn":              # controlled
            # end turn if rolled
            if self.active_user_state != TURN_STATE.buy_wait:
                raise WrongStateException("Can not end turn if roll or teleport is needed")
            self.next_user()
            '''elif command == "List":
            self.getboardstate()
            print("")
            self.getuserstate(user)
            print("")'''
        else:
            raise WrongCommandException("Your command: \""+command+"\" is not valid")


        # Goes bankrupt if no money is left
        if self.user_dict[user]["money"]<0: # controlled
            self.detach(user)

        self.print_report(user)

        return self.order[self.active_user_index]
    def execute_cell(self,current_user_dict,cell):      # controlled
        if cell["type"]=="start":       # controlled
            self.next_user()
        elif cell["type"]=="jail":      # controlled
            self.next_user()
        elif cell["type"]=="tax":       # controlled
            current_user_dict["money"]-=self.tax*len(current_user_dict["properties"])
            self.next_user()
        elif cell["type"]=="gotojail":  # controlled
            # find nearest jail cell then go(it goes on your record ) )
            mypos=current_user_dict["position"]
            for addition in range(self.N):
                if self.cells[(mypos+addition)%self.N]["type"]=="jail":
                    j_hi=addition
                    break
            for addition in range(self.N):
                if self.cells[(mypos-addition+self.N)%self.N]["type"]=="jail":
                    j_lo=addition
                    break
            if j_hi<j_lo:
                jail_pos=(mypos+j_hi)%self.N
            else:
                jail_pos=(mypos-j_lo+self.N)%self.N
            current_user_dict["position"]=jail_pos
            current_user_dict["guilty"]=True
            self.next_user()
        elif cell["type"]=="teleport":  # controlled
            #implementation at turn
            current_user_dict["money"]-=self.teleport

            self.active_user_state=TURN_STATE.teleport_wait
        elif cell["type"]=="property":  # controlled
            current_property=cell["property"]
            if current_property.owner==None:
                self.active_user_state = TURN_STATE.buy_wait
            elif current_property.owner!=current_user_dict["user"]:
                current_property.pay_current_rent(current_user_dict, self.user_dict[current_property.owner])
                self.next_user()
            else: #if user owns it
                self.next_user()
        elif cell["type"]=="chance":
            card_number = take_chance_card()
            card = self.chance_card_list.get()
            NEXT_USER_FLAG=True
            PUT_CARD_BACK_FLAG=True

            if card == 'upgrade' or card == 'downgrade':    # controlled
                '''selected_cell = int(input('select a cell to upgrade'))
                self.turn(current_user_dict['user'], f'Pick{selected_cell}-{card_number}')'''
                owns_property = len(current_user_dict["user"]["properties"])
                while owns_property:
                    response_string = input('select a cell you own to'+ card+'(in the form Pick(cell number)):')
                    if not (response_string.startswith("Pick(") and
                            response_string.endswith(")") and
                            response_string[5:-1].isnumeric()):
                        continue
                    cell_index=int(response_string[5:-1])
                    if self.cells[cell_index]["type"] != "property":
                        continue

                    current_property = self.cells[cell_index]["property"]
                    if current_property.owner != user:
                        continue
                    if card == 'upgrade':
                        current_property.upgrade()
                    elif card == 'downgrade':
                        current_property.downgrade()
                    break

            elif card == 'color_upgrade' or card == 'color_downgrade':  # controlled
                owns_property=len(current_user_dict["user"]["properties"])
                while owns_property:
                    selected_color = input('select a color to'+ card[6:] +'that you have at least one property:')
                    if selected_color not in self.color_list:
                        continue
                    flag=False
                    for prop in self.properties_by_color[selected_color]:
                        if prop.owner==current_user_dict["user"]:
                            flag=True
                            break
                    if flag==False:
                        continue
                    for prop in self.properties_by_color[selected_color]:
                        if card == 'color_upgrade':
                            prop.upgrade()
                        if card == 'color_downgrade':
                            prop.downgrade()

            elif card == 'gotojail':            # controlled
                mypos = current_user_dict["position"]
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

            elif card == 'jail_free':           # controlled
                current_user_dict['jailFree'] += 1
                PUT_CARD_BACK_FLAG=False

            elif card == 'teleport':            # controlled
                '''selected_cell = int(input('select a cell to teleport'))
                self.turn(current_user_dict['user'], f'Teleport{selected_cell}')'''
                self.active_user_state = TURN_STATE.teleport_wait
                NEXT_USER_FLAG=False

            elif card == 'lottery':             # controlled
                current_user_dict['money'] += self.lottery
            elif card == 'tax':                 # controlled
                current_user_dict["money"] -= self.tax * len(current_user_dict["properties"])

            if(NEXT_USER_FLAG):
                self.next_user()
            if(PUT_CARD_BACK_FLAG):
                self.chance_card_list.put(card)
    def getuserstate(self, user):       # controlled
        #print({k.username: {'money': v['money'], 'properties': [str(prop) for prop in v['properties']]} for k, v in self.user_dict.items()})
        for k, v in self.user_dict.items():
            print({k.username: {'money': v['money']}})
            for prop in v['properties']:
                print("\t",prop.user_visualization())
    def getboardstate(self):            # controlled
        for property in self.properties:
            print(property)
    def print_report(self,user):
        self.getboardstate()
        print("")
        self.getuserstate(user)
        print("")

        print("LAST PLAY:\t{:<{uL}} position: {:<{pL}} cell: {}".format(
            user.username,
            self.user_dict[user]["position"],
            self.cells[self.user_dict[user]["position"]],
            uL=20,
            pL=3
        ))
        print("TURN ON:\t{:<{uL}} position: {:<{pL}} cell: {:<{cL}}".format(
            self.order[self.active_user_index].username,
            self.user_dict[self.order[self.active_user_index]]["position"],
            str(self.cells[self.user_dict[self.order[self.active_user_index]]["position"]]),
            uL = 20,
            pL = 3,
            cL = 20
        ))
        print("")
    def ListCommands(self,user):
        print(user.username,end=" ")
        if self.user_dict[user]["guilty"]:
            print("You are at jail")
            print("You have "+ self.user_dict[user]["jailFree"] +" jailFree cards")
            print("Avaliable commands to you are:")
            print("\tRoll")
            print("\tBail")
        elif self.active_user_state == TURN_STATE.turn_start:
            print("You are at start of the turn")
            print("Avaliable commands to you are:")
            print("\tRoll")
        elif self.active_user_state == TURN_STATE.teleport_wait:
            print("You are in teleportation state")
            print("Avaliable commands to you are:")
            print("\tTeleport(index)")
        elif self.active_user_state == TURN_STATE.buy_wait:
            print("You are in last state")
            print("Avaliable commands to you are:")
            print("\tEndTurn")
            if (self.cells[self.user_dict[user]["position"]]["property"].owner == None):
                print("\tBuy")
            else:
                print("\tUpgrade")
        print("")
    def next_user(self):                # controlled
        n=len(self.order)
        self.active_user_index=(self.active_user_index+1)%n
        self.active_user_state = TURN_STATE.turn_start


class Property:
    max_level=5
    def __init__(self,prop_dict):
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
            "owner": self.owner.username if self.owner!=None else None,
            "level": self.level,
        })
    def user_visualization(self):
        return str({
            "name": self.name,
            "current rent": self.get_current_rent(),
            "level": self.level,
        })
    def get_current_rent(self):
        return self.rents[self.level-1]
    def pay_current_rent(self,renter_user_dict,owner_user_dict):
        if(owner_user_dict["guilty"]==False):
            renter_user_dict["money"] -= self.rents[self.level-1]
            owner_user_dict["money"]  += self.rents[self.level-1]
    def at_max_level(self):
        return (self.level>=self.max_level)
    def at_min_level(self):
        return (self.level==1)

    '''def __repr__(self):             #TODO using like this might create problems
        return self.__str__()'''
    def upgrade(self):
        if self.level<self.max_level:
            self.level+=1
    def downgrade(self):
        if self.level>1:
            self.level-=1


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


class TURN_STATE(Enum):
    turn_start = 1
    teleport_wait = 2
    buy_wait =3


#raise UPoorException()
