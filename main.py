from Board import Board
from User import User

#-------------------------------------------------------------------------------------
'''

In class library phase you should implement your basic classes and write a command
line test application demonstrating all features of your library.

'''
#-------------------------------------------------------------------------------------




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

monopoly.ready(user1)
monopoly.ready(user2)

monopoly.getboardstate()
print("")
monopoly.getuserstate(user1)

current_user=user1
print("------------------------------------------------------------------------------------")
while True:
    monopoly.getboardstate()
    monopoly.getuserstate(user1)
    current_user=monopoly.turn(current_user, input())

