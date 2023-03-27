import json
import copy


class Board:

    def __init__(self,file):
        data=json.loads(file.read())

        self.cells=data["cells"]
        self.upgrade = data["upgrade"]
        self.teleport = data["teleport"]
        self.jailbail = data["jailbail"]
        self.tax = data["tax"]
        self.lottery = data["lottery"]
        self.startup = data["startup"]
        self.chance_card_list=data["chances"]

        self.properties=[]
        self.get_properties()

        self.user_dict={}
        self.unready_count=0

    def get_properties(self):
        for cell in self.cells:
            if cell['type']=='property':
                cellV2=copy.deepcopy(cell)
                cellV2['owner']=None
                cellV2['level']=0
                del cellV2['type']
                self.properties.append(cellV2)

    def attach(self, user, callback):
        self.user_dict[user]={"user":user,
                              "money":self.startup,
                              "position":0,
                              "properties":[],
                              "ready":False}
        self.unready_count+=1
        # TODO whatever callback is
    def detach(self, user):
        if user in self.user_dict:
            del self.user_dict[user]
    def ready(self, user):
        if self.user_dict[user]["ready"]==False:
            self.user_dict[user]["ready"]=True
            self.unready_count-=1
            if (self.unready_count==0 and len(self.user_dict)>=2):


        pass  # TODO
    def turn(self, user, command):
        pass  # TODO
    def getuserstate(self, user):
        return {k: {'money': v['money'], 'properties': v['properties']} for k, v in self.user_dict.items()} #TODO might need to add levels
    def getboardstate(self):
        return self.properties


'''
attach(user, callback,
turncb)
User attaches to an existing board. Board events are sent to
callback function
detach(user) User detaches from the board. If game is started, all properties
and money is returned as initialized
ready(user) The attached user mark himself/herself as ready. When the all
attached users mark the game ready, game starts.
turn(user, command) When users turn, user gives the command/choice for his/her
turn
getuserstate(user) Generate a report for each user, money and properties with
their levels
getboardstate() Generates a report for the board, properties, their level and
owner
'''




file=open("board_in","r")
Board(file)