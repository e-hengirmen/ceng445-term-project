from Board import Board
from User import User
import sys
import os
import socket

import threading as th

#-------------------------------------------------------------------------------------
'''

In class library phase you should implement your basic classes and write a command
line test application demonstrating all features of your library.

'''
#-------------------------------------------------------------------------------------
PORT=3333
number_of_users=2


for i in range(len(sys.argv)):
    if sys.argv[i]=="--port":
        PORT=int(sys.argv[i+1])
        break
'''for i in range(len(argv)):
    if argv[i]=="-n":
        number_of_users=int(argv[i+1])
        break'''

if(2>number_of_users or number_of_users>4):
    print("number of users should be between 2 and 4")
    exit()
file=open("../gameBoards/deneme_in","r")
monopoly=Board(file,number_of_users)



# Server start
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind socket to a specific address and port
server_socket.bind(('', PORT))

'''#-----------------------------------------------------
# Server start
server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
# bind socket to a specific address and port
os.remove("/tmp/mysocket")
server_socket.bind("/tmp/mysocket")
#-----------------------------------------------------
'''



# listen for incoming connections
server_socket.listen(10)
print(f"Server listening on port {PORT}")


#-----------------------------user thread function--------------------------------------------
def user_thread_func(client_socket, address, monopoly):

    # create new thread to handle client request    # TODO for failed user initiation try except with number of users unchanigng
    user = User(client_socket, address)

    # attaching user
    monopoly.attach(user, user.callback, user.turncb)

    # wait for user to respond with ready
    user.client_socket.send("write \"ready\" when you are\n".encode('utf-8'))
    ready_msg = user.client_socket.recv(1024).decode('utf-8').strip()
    while ready_msg!="ready":
        user.client_socket.send(f"Invalid message {ready_msg}. say \"ready\" when you are ready\n".encode('utf-8'))
        ready_msg = user.client_socket.recv(1024).decode('utf-8').strip()
    monopoly.ready(user)

    # barrier waiting it will be opened by the last user in board
    if monopoly.WaitingState==True:
        user.mutex.acquire()




#---------------------------------------------------------------------------------------------



user_threads=[]
for i in range(number_of_users):
    # accept incoming connection
    client_socket, address = server_socket.accept()
    print(f"Accepted connection from {address}")

    user_thread=th.Thread(target=user_thread_func,args=(client_socket, address, monopoly))
    user_threads.append(user_thread)
    user_thread.start()
# close socket
server_socket.close()

for user_thread in user_threads:
    user_thread.join()




current_user=monopoly.order[0]
while True:
    current_user=monopoly.turn(current_user)
    if(current_user==None):
        break

