import json
from User import User
import random
from enum import Enum




def roll_a_dice():
    return random.randint(1, 6)

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
        self.chance_card_list=data["chances"]   #used as chance card list which it is

        # property user containers
        self.properties=[]
        self.user_dict={}
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


    def get_properties(self):
        for cell in self.cells:
            if cell['type']=='property':
                current_property=Property(cell)
                cell['property']=current_property
                self.properties.append(current_property)


    def attach(self, user, callback,turncb):
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
    def detach(self, user):
        if user in self.user_dict:
            del self.user_dict[user]
            self.order.remove(user)
            for prop in self.user_dict[user]["properties"]:
                prop.owner=None
            self.next_user()
    def ready(self, user):
        if self.user_dict[user]["ready"]==False:
            self.user_dict[user]["ready"]=True
            self.unready_count-=1
            if (self.unready_count==0 and len(self.user_dict)>=2):
                self.initiate_game()
    def initiate_game(self):
        self.WaitingState=False
    def turn(self, user, command):
        if self.WaitingState==True:
            raise WaitingForReadyException()
        if self.order[self.active_user_index]!=user:
            print(self.active_user_index,user)
            raise NotYourTurnException()
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
                else:
                    self.user_dict[user]["money"] -= self.jailbail
                self.user_dict[user]["guilty"] = False
            else:
                raise WrongCommandException("you're in jail, your command was \{{}\} it should either be Roll or Bail".format(command))
            self.next_user()

        #normal roll
        elif command == "Roll":
            if self.active_user_state!=TURN_STATE.turn_start:
                raise WrongStateException()
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
        elif command == "Buy":
            if self.active_user_state!=TURN_STATE.buy_wait:
                raise WrongStateException()
            if self.cells[self.user_dict[user]["position"]]["type"]!="property":
                raise NotPropertyException()

            current_user_dict = self.user_dict[user]
            position=current_user_dict["position"]
            current_property = self.cells[position]["property"]

            if current_property.owner != None:
                raise AlreadyOwnedException()
            if current_property.price>current_user_dict["money"]:
                raise UPoorException()



            current_user_dict["money"]-=current_property.price
            current_user_dict["properties"].append(current_property)
            current_property.owner=user

            self.next_user()
        elif command == "Upgrade":
            if self.active_user_state!=TURN_STATE.buy_wait:
                raise WrongStateException()
            if self.cells[self.user_dict[user]["position"]]["type"] != "property":
                raise NotPropertyException()
            current_user_dict = self.user_dict[user]
            position = current_user_dict["position"]
            current_property = self.cells[position]["property"]
            if current_property.owner!=user:
                raise NotOwnedException()
            if current_property.at_max_level():
                raise MaxLevelException()
            if self.upgrade>current_user_dict["money"]:
                raise UPoorException()
            current_user_dict["money"] -= current_property.price
            current_property.upgrade()
            self.next_user()
        elif command.startswith("Pick"):#"Pick(property)" #TODO add next state or change user in execute chance card
            picked_cell_index = int(command[5:-1])
            execute_chance_card(self.chosen_chance_card,picked_cell_index)
        elif command.startswith("Teleport"):#"Teleport(Newcell)":
            next_cell_index = int(command[9:-1])
            if self.cells[next_cell_index]["type"]!="property":
                raise NotPropertyException()

            self.user_dict[user]["position"] = next_cell_index

            current_property = self.cells[next_cell_index]["property"]
            if current_property.owner == None:
                self.active_user_state = TURN_STATE.buy_wait
            elif current_property.owner != current_user_dict["user"]:
                current_user_dict["money"] -= current_property.get_current_rent()
                self.next_user()
        elif command == "EndTurn":
            self.next_user()
        else:
            raise WrongCommandException("you're in jail, your command was \{{}\} it should either be Roll or Bail".format(command))


        # Goes bankrupt if no money is left
        if self.user_dict[user]["money"]<0:
            self.detach(user)

        print("END:",user.username,"position",self.user_dict[user]["position"],"cell:",self.cells[self.user_dict[user]["position"]])
        print("turn on:",self.order[self.active_user_index].username,
              "position",self.user_dict[self.order[self.active_user_index]]["position"],
              "cell:",self.cells[self.user_dict[self.order[self.active_user_index]]["position"]])
        return self.order[self.active_user_index]

    def execute_cell(self,current_user_dict,cell):
        if cell["type"]=="start":
            self.next_user()
        elif cell["type"]=="jail":
            self.next_user()
        elif cell["type"]=="tax":
            current_user_dict["money"]-=self.tax*len(current_user_dict["properties"])
            self.next_user()
        elif cell["type"]=="gotojail":
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
        elif cell["type"]=="teleport":
            #implementation at turn
            current_user_dict["money"]-=self.teleport

            self.active_user_state=TURN_STATE.teleport_wait
        elif cell["type"]=="property":
            current_property=cell["property"]
            if current_property.owner==None:
                self.active_user_state = TURN_STATE.buy_wait
            elif current_property.owner!=current_user_dict["user"]:
                current_user_dict["money"]-=current_property.get_current_rent()
                self.next_user()

        #elif property["type"]=="chance":   #TODO

    def execute_chance_card(self,card,cell_index):
        pass    # TODO
    def getuserstate(self, user):
        #print({k.username: {'money': v['money'], 'properties': [str(prop) for prop in v['properties']]} for k, v in self.user_dict.items()})
        for k, v in self.user_dict.items():
            print({k.username: {'money': v['money']}})
            for prop in v['properties']:
                print("\t",prop)
    def getboardstate(self):
        for property in self.properties:
            print(property)
    def next_user(self):
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
    def get_current_rent(self):
        return self.rents[self.level-1]
    def at_max_level(self):
        return (self.level<self.max_level)

    '''def __repr__(self):             #TODO using like this might create problems
        return self.__str__()'''
    def upgrade(self):
        if self.level<self.max_level:
            self.level+=1
    def downgrade(self):
        if self.level>1:
            self.level-=1


class NotOwnedException(BaseException):
    pass
class AlreadyOwnedException(BaseException):
    pass
class NotPropertyException(BaseException):
    pass
class UPoorException(BaseException):
    pass
class WrongStateException(BaseException):
    pass
class WaitingForReadyException(BaseException):
    pass
class NotYourTurnException(BaseException):
    pass

class MaxLevelException(BaseException):
    pass


class TURN_STATE(Enum):
    turn_start = 1
    teleport_wait = 2
    buy_wait =3


#raise UPoorException()
