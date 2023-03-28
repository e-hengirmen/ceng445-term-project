import json
from User import User
import random


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
        self.active_user_state=0

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
                              "ready":False,}
        self.unready_count+=1
        self.order.append(user)
        # TODO whatever callback is
    def detach(self, user):
        if user in self.user_dict:
            del self.user_dict[user]
            self.order.remove(user)
    def ready(self, user):
        if self.user_dict[user]["ready"]==False:
            self.user_dict[user]["ready"]=True
            self.unready_count-=1
            if (self.unready_count==0 and len(self.user_dict)>=2):
                self.initiate_game()
    def initiate_game(self):
        self.WaitingState=False
    def turn(self, user, command):
        if command == "Roll":
            dice1=roll_a_dice()
            dice2=roll_a_dice()
            #show_dice_roll(dice1,dice2)
            roll_res=dice1+dice2
            self.user_dict[user]["position"]=(self.user_dict[user]["position"]+roll_res)
            if self.user_dict[user]["position"]>=self.N:
                self.user_dict[user]["position"]-=self.N
                self.user_dict[user]["money"]+=self.lapping_salary
            #self.execute_cell(self.user_dict[user]["position"])
            self.execute_cell(user,self.cells[self.user_dict[user]["position"]])
        elif command == "Buy":
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


        elif command == "Upgrade":
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
        #elif command == "Pick(property)":# TODO
        #elif command == "Bail":# TODO
        #elif command == "Teleport":  # TODO
        #elif command == "EndTurn":# TODO

        #pass    # TODO
    def execute_cell(self,user,cell):
        if cell["type"]=="start":
            return
        #elif property["type"]=="property":
        #elif property["type"]=="teleport":
        #elif property["type"]=="tax":
        #elif property["type"]=="jail":
        #elif property["type"]=="gotojail":
        #elif property["type"]=="chance":
        '''
        { "type": "start"},
          { "type": "property", "name": "bostanci", "cell": 2, "color": "red",
            "price":120, "rents": [50,150,400,600,900]},
          { "type": "teleport"}, {"type": "tax"}, {"type": "jail"}],
        '''
        pass    # TODO
    def getuserstate(self, user):
        print({k.username: {'money': v['money'], 'properties': v['properties']} for k, v in self.user_dict.items()})
        '''for k, v in self.user_dict.items():
            print({
                "username": k.username,
                "money": v["money"],
                "properties": v["properties"],

            })'''
    def getboardstate(self):
        for property in self.properties:
            print(property)



class Property:
    max_level=4
    def __init__(self,prop_dict):
        self.name = prop_dict["name"]
        self.cell = prop_dict["cell"]
        self.color = prop_dict["color"]
        self.price = prop_dict["price"]
        self.rents = prop_dict["rents"]

        self.owner = None
        self.level = 0
    def __str__(self):
        max_level=4
        return str({
            "name": self.name,
            "cell": self.cell,
            "color": self.color,
            "price": self.price,
            "rents": self.rents,
            "owner": self.owner.username if self.owner!=None else None,
            "level": self.level,
        })
    def at_max_level(self):
        return (self.level<self.max_level)

    def __repr__(self):             #TODO using like this might create problems
        return self.__str__()
    def upgrade(self):
        if self.level<self.max_level:
            self.level+=1
    def downgrade(self):
        if self.level>0:
            self.level-=1


class NotOwnedException(BaseException):
    pass
class AlreadyOwnedException(BaseException):
    pass
class NotPropertyException(BaseException):
    pass
class UPoorException(BaseException):
    pass


class MaxLevelException(BaseException):
    pass



#raise UPoorException()
