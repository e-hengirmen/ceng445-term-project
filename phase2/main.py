from Board import Board
from User import User
import sys

#-------------------------------------------------------------------------------------
'''

In class library phase you should implement your basic classes and write a command
line test application demonstrating all features of your library.

'''
#-------------------------------------------------------------------------------------

if(len(sys.argv)<1):
    print("use this program in the form:")
    print("python3 demo.py {input_fie_name}")
file=open(sys.argv[1],"r")
monopoly=Board(file)

print("--------------------User print control--------------------")
user1=User("ehengirmen","ehengirmen@hotmail.com","Ersel","ABCDEF")
user2=User("mert","mert@hotmail.com","Mert","zzzzzz")
print(user1)
print(user2)
print("----------------------------------------------------------")
print("")

monopoly.attach(user1,user1.callback,user1.turncb)
monopoly.attach(user2,user2.callback,user2.turncb)


print("------------------------------------------------------------------------------------")
monopoly.ready(user1)
monopoly.ready(user2)

print("")
#monopoly.getboardstate()
#monopoly.getuserstate(user1)

current_user=user1
while True:
    current_user=monopoly.turn(current_user)
    if(current_user==None):
        break

