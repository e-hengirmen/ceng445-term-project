from Board import Board
from User import User







file=open("board_in","r")
monopoly=Board(file)

print("--------------------User print control--------------------")
user1=User("ehengirmen","ehengirmen@hotmail.com","Ersel","ABCDEF")
user2=User("mert","mert@hotmail.com","Mert","zzzzzz")
print(user1)
print(user2)
print("----------------------------------------------------------")
print("")

print("--------------------board initial getboardstate and getuserstate--------------------")
monopoly.attach(user1,0,0)
monopoly.attach(user2,0,0)
monopoly.getboardstate()
print("")

monopoly.getuserstate(user1)
print("------------------------------------------------------------------------------------")
print("")
