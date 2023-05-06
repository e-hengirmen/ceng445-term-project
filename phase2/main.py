from Board import Board
from User import User
from Server import Server

import sys
import os
import socket
import json

import threading as th

#-------------------------------------------------------------------------------------
'''

In class library phase you should implement your basic classes and write a command
line test application demonstrating all features of your library.

'''
#-------------------------------------------------------------------------------------
PORT=3333
filename="../gameBoards/deneme_in"

for i in range(len(sys.argv)):
    if sys.argv[i]=="--port":
        PORT=int(sys.argv[i+1])
        break




# Creating server
server=Server()

# Server socket starts
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
server_socket.listen()
print(f"Server listening on port {PORT}")


def become_playing_thread(monopoly,user):
    while True:
        game_state = monopoly.turn(user)
        if (game_state == None):
            break
def become_observer_thread(monopoly,user):
    # TODO
    x=3
def become_game_thread(monopoly):
    current_user = monopoly.order[0]
    while True:
        current_user = monopoly.turn(current_user)
        if (current_user == None):
            break

#-----------------------------user thread function--------------------------------------------
def user_thread_func(client_socket, address):

    # ask sign in or up:
    while True:
        wrong_count=0
        client_socket.send("Do u want to login or sign up or exit:write either \"login\" or \"sign up\" or \"exit\"\n".encode("utf-8"))
        received_msg = client_socket.recv(1024).decode('utf-8').strip()
        if(received_msg=="login"):
            user = User(client_socket, address, "login")
            if(user.authh()==False):
                client_socket.send("Wrong password or Username goodbye\n".encode("utf-8"))
                return
            break
        elif(received_msg=="sign up"):
            user = User(client_socket, address,"sign up")
        elif(received_msg == "exit"):
            client_socket.send("Goodbye and have a nice day\n".encode("utf-8"))
            return
        else:
            wrong_count+=1
            if(wrong_count<3):
                client_socket.send(f"You wrote {received_msg} wrong input count={wrong_count}\n".encode("utf-8"))
            else:
                client_socket.send(f"You wrote {received_msg} wrong input count={wrong_count} goodbye\n".encode("utf-8"))
                return


    while True:
        # sending game list to the user
        this_thread_is_observer_thread=False
        while True:
            is_user_attached=False
            game_list=server.list()
            user.client_socket.send(("New or join or observe\nto exit write exit\nto join write Join(game_id)\nto observe write Observe(game_id)\nto create a game New(number of players)\n\tnumber of players must be between 2-4\n"+str(game_list)+"\n").encode("utf-8"))
            received_msg = user.client_socket.recv(1024).decode('utf-8').strip()
            if received_msg.startswith("New(") and received_msg.endswith(")") and received_msg[4:-1].isnumeric():
                user_count = int(received_msg[4:-1])
                monopoly=server.new(user_count)
                if monopoly:
                    is_user_attached=server.open(monopoly, user)
                    # is_user_attached=True
            elif received_msg.startswith("Join(") and received_msg.endswith(")") and received_msg[5:-1].isnumeric():
                game_index=int(received_msg[5:-1])
                if(game_index in game_list):
                    is_user_attached=server.open(game_list[game_index],user)
                    if(is_user_attached):
                        monopoly=game_list[game_index]
                else:
                    user.client_socket.send(f"There is no game ({game_index})\n".encode("utf-8"))
            elif received_msg.startswith("Observe(") and received_msg.endswith(")") and received_msg[8:-1].isnumeric():
                game_index=int(received_msg[8:-1])
                if(game_index in game_list):
                    server.observe(game_list[game_index],user)
                    this_thread_is_observer_thread=True
                    is_user_attached=True
                else:
                    user.client_socket.send(f"There is no game ({game_index})\n".encode("utf-8"))
            elif (received_msg == "exit"):
                client_socket.send("Goodbye and have a nice day\n".encode("utf-8"))
                return
            else:
                user.client_socket.send(f"Sent wrong commend({received_msg})\n".encode("utf-8"))
            if(is_user_attached):
                break

        if(this_thread_is_observer_thread==True):
            become_observer_thread(monopoly,user)
            continue





        # wait for user to respond with ready
        user.client_socket.send("write \"ready\" when you are ready write \"exit\" if you want to leave\n".encode('utf-8'))
        ready_msg = user.client_socket.recv(1024).decode('utf-8').strip()
        while ready_msg!="ready" and ready_msg!="exit":
            user.client_socket.send(f"Invalid message {ready_msg}. write \"ready\" when you are ready write \"exit\" if you want to leave\n".encode('utf-8'))
            ready_msg = user.client_socket.recv(1024).decode('utf-8').strip()
        if ready_msg == "exit":
            server.close(monopoly,user)
            continue
        monopoly.ready(user)



        # barrier waiting it will be opened by the last user in board
        '''if monopoly.WaitingState==True:
            user.mutex.acquire()
        else:
            become_game_thread(monopoly)'''
        become_playing_thread(monopoly,user)




#---------------------------------------------------------------------------------------------



user_threads=[]
while True:
    # accept incoming connection
    client_socket, address = server_socket.accept()
    print(f"Accepted connection from {address}")

    user_thread=th.Thread(target=user_thread_func,args=(client_socket, address))
    user_threads.append(user_thread)
    user_thread.start()

for user_thread in user_threads:
    user_thread.join()




'''current_user=monopoly.order[0]
while True:
    current_user=monopoly.turn(current_user)
    if(current_user==None):
        break'''

