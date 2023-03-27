import json
import copy
from User import User

class Board:

    def __init__(self,file):
        data=json.loads(file.read())

        # file variables
        self.cells=data["cells"]
        self.upgrade = data["upgrade"]
        self.teleport = data["teleport"]
        self.jailbail = data["jailbail"]
        self.tax = data["tax"]
        self.lottery = data["lottery"]
        self.startup = data["startup"]
        self.chance_card_list=data["chances"]

        # property user containers
        self.properties=[]
        self.user_dict={}
        self.get_properties()

        # state variables
        self.unready_count=0
        self.WaitingState=True

        #
        self.order=[]
        self.current_player_index=0


    def get_properties(self):
        for cell in self.cells:
            if cell['type']=='property':
                self.properties.append(Property(cell))

    def attach(self, user, callback,turncb):
        self.user_dict[user]={"user":user,
                              "money":self.startup,
                              "position":0,
                              "properties":[],
                              "ready":False}
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
        pass  # TODO
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
    def __init__(self,prop_dict):
        self.name = prop_dict["name"]
        self.cell = prop_dict["cell"]
        self.color = prop_dict["color"]
        self.price = prop_dict["price"]
        self.rents = prop_dict["rents"]

        self.owner = None
        self.level = 0
    def __str__(self):
        return str({
            "name": self.name,
            "cell": self.cell,
            "color": self.color,
            "price": self.price,
            "rents": self.rents,
            "owner": self.owner,
            "level": self.level,
        })





