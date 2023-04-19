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
    print("python3 main.py {input_fie_name}")
file=open(sys.argv[1],"r")
monopoly=Board(file)

print("--------------------User print control--------------------")
user1=User("ehengirmen","ehengirmen@hotmail.com","Ersel","ABCDEF")
user2=User("mert","mert@hotmail.com","Mert","zzzzzz")
print(user1)
print(user2)
print("----------------------------------------------------------")
print("")

monopoly.attach(user1,user1.callback,user1.turncb2)
monopoly.attach(user2,user2.callback,user2.turncb2)
"""
1-buy illionios
2-buy vermont
3-tax
4-take a lap, Teleport to Vermont, upgrade
5-gotojail
6-ROlled 6 6 out of jail
7-take a lap, went to Vermont, upgrade
8-take a lap, went to Vermont, upgrade
9-take a lap, went to Vermont, EndTurn
10-take a lap, went to Vermont, upgrade
11-take a lap, went to Vermont, EndTurn
12-Chance(Teleport),Teleport to Vermont, try upgrade, max level fail,EndTurn
13-Chance(lottery)
14-take a lap, Chance(tax)
15-take a lap twice,start
15-take a lap,start
"""
user1.setCommandList(["Roll(2)","Buy",
                      "Roll(2)","Buy",
                      "Roll(3)",
                      "Roll(11)","Teleport(5)","Upgrade",
                      "Roll(2)",
                      "DoubleDice",
                      "Roll(9)","Upgrade",
                      "Roll(10)","Upgrade",
                      "Roll(10)","EndTurn",
                      "Roll(10)","Upgrade",
                      "Roll(10)","EndTurn",
                      "Roll(5)","Teleport(5)","Upgrade","EndTurn",
                      "Roll(5)",
                      "Roll(10)",
                      "Roll(11)",
                      "Roll(10)",
                      ])
"""
1-Buy Atlantic
2-failed command,gotojail
3-Rolled 3 5 still in jail
4-Bailed
5-Went to vermont,didnt pay rent since ehengirmen was in jail
6-Chance,upgrade card on(Atlantic,4)
7-Chance,downgrade card on(Atlantic,4)
8-Chance,upgrade color card on(blue)
9-Chance,upgrade color card on(red) fail, upgrade color card on(blue),
10-Chance, get jailfree 
11-Chance, goto jail
12-Bail(pays with jailfree card
13- Teleport to Vermont(pay a lot)
14-Teleport to Vermont(pay a lot)
15-Teleport to Vermont(pay a lot)
16-Teleport to Vermont(pay a lot)
"""
user2.setCommandList(["Roll(3)","Buy",
                      "asdsads","Roll(3)",
                      "NotDoubleDice",
                      "Bail",
                      "Roll(9)",
                      "Roll(5)","Pick(4)",
                      "Roll(10)","Pick(4)",
                      "Roll(10)","red","blue",
                      "Roll(10)","blue",
                      "Roll(10)",
                      "Roll(10)",
                      "Bail",
                      "Roll(3)","Teleport(5)",
                      "Roll(4)","Teleport(5)",
                      "Roll(4)","Teleport(5)",
                      ])


print("------------------------------------------------------------------------------------")
monopoly.ready(user1)
monopoly.ready(user2)

print("")
#monopoly.getboardstate()
#monopoly.getuserstate(user1)

current_user=user1
i=0
while True:
    current_user=monopoly.turn(current_user)
    if(current_user==None):
        break
    i+=1

