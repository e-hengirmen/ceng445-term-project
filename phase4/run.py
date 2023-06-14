import asyncio
import json
import websockets

from Board import Board
from User import User
from Server import Server

# Server class
server = Server()




async def become_user_thread(game,user,websocket):
    if game.WaitingState==True:
        print(game.user_dict)
        if not game.user_dict[user]["ready"]:
            await websocket.send(f'{{"state":"readywait","possible_commands":["ready","exit"]}}')

            ready_msg = await websocket.recv()
            ready_msg = ready_msg.strip()

            while ready_msg != "ready" and ready_msg != "exit":
                await websocket.send(f'{{"state":"readywait","possible_commands":["ready","exit"]}}')
                ready_msg = await websocket.recv()
                ready_msg = ready_msg.strip()

            if ready_msg == "exit":
                server.close(game, user)
                return
            game.ready(user)

    while True:
        # await websocket.send(game.text_game_state(user))
        if(game.WaitingState):
            await websocket.send(f'{{"state":"readywait","possible_commands":["exit"]}}')
        for user in game.user_dict:
            WEBSOCKET=game.user_dict[user]["callback"]
            if (game.game_has_ended):
                await WEBSOCKET.send(f'{{"state":"ended","winner":game.winner,"possible_commands":["exit"]}}')
            elif(game.WaitingState==False):
                await WEBSOCKET.send(f'{{"state":"ingame","possible_commands":{game.getCommands(user)}}}')

        command=await websocket.recv()
        game.turn(user,command)
        if (game.game_has_ended):
            await websocket.send(f'{{"state":"ended","winner":game.winner,"possible_commands":["exit"]}}')
        if command=="exit":
            del server.user_connection[user]
            break




async def become_observer_thread(game,user):
    pass


async def list_server(websocket,user):
    while True:
        this_thread_is_observer_thread=False
        is_user_attached=False
        while True:
            # Send game list to the user
            game_list = server.list()
            str_game_list= {str(i):str(game_list[i]) for i in game_list}
            str_game_list=str(str_game_list).replace("'", '"' )
            await websocket.send(f'{{"state":"server","game_list":{str_game_list}}}')

            received_msg = await websocket.recv()
            received_msg = received_msg.strip()
            print(received_msg)
            if received_msg.startswith("New(") and received_msg.endswith(")") and received_msg[4:-1].isnumeric():
                user_count = int(received_msg[4:-1])
                monopoly = server.new(user_count)

            elif received_msg.startswith("Join(") and received_msg.endswith(")") and received_msg[5:-1].isnumeric():
                game_index = int(received_msg[5:-1])
                if game_index in game_list:
                    is_user_attached = server.open(game_list[game_index], user,websocket)
                    monopoly = game_list[game_index]

            elif received_msg.startswith("Observe(") and received_msg.endswith(")") and received_msg[8:-1].isnumeric():
                game_index = int(received_msg[8:-1])
                if game_index in game_list:
                    server.observe(game_list[game_index], user,websocket)
                    monopoly = game_list[game_index]
                    this_thread_is_observer_thread = True
                    is_user_attached = True
            if(is_user_attached):
                    break

        if this_thread_is_observer_thread:
            await become_observer_thread(monopoly, user,websocket)
        else:
            await become_user_thread(monopoly,user,websocket)

# Function to handle incoming WebSocket connections
async def handle_websocket(websocket, path):
    # Create a new user for the WebSocket connection
    user = await websocket.recv()

    if server.IfUserInGame(user):
        monopoly=server.user_connection[user]
        await become_user_thread(monopoly,user,websocket)
    elif server.IfObserverInGame(user):
        aaaaa=3+3   #TODO


    await list_server(websocket,user)



    






# Start the WebSocket server
async def start_websocket_server():
    server = await websockets.serve(handle_websocket, "localhost", 4444)

    # Keep the server running indefinitely
    await server.wait_closed()

# Run the WebSocket server
asyncio.run(start_websocket_server())