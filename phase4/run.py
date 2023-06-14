import asyncio
import json
import websockets

from Board import Board
from User import User
from Server import Server

# Server class
server = Server()




async def become_user_thread(game,user):
    if game.WaitingState==True:
        await websocket.send("Write 'ready' when you are ready. Write 'exit' if you want to leave.")

        ready_msg = await websocket.recv()
        ready_msg = ready_msg.strip()

        while ready_msg != "ready" and ready_msg != "exit":
            await websocket.send(f"Invalid message: {ready_msg}. Write 'ready' when you are ready. Write 'exit' if you want to leave.")
            ready_msg = await websocket.recv()
            ready_msg = ready_msg.strip()

        if ready_msg == "exit":
            server.close(monopoly, user)
            return

    while True:
        game_state = monopoly.turn(user)
        if (game_state == None):
            break



async def become_observer_thread(game,user):
    pass


async def list_server(websocket,user):
    this_thread_is_observer_thread=False
    is_user_attached=False
    while True:
        # Send game list to the user
        game_list = server.list()
        await websocket.send(f"{game_list}")

        received_msg = await websocket.recv()
        received_msg = received_msg.strip()

        if received_msg.startswith("New(") and received_msg.endswith(")") and received_msg[4:-1].isnumeric():
            user_count = int(received_msg[4:-1])
            monopoly = server.new(user_count)

        elif received_msg.startswith("Join(") and received_msg.endswith(")") and received_msg[5:-1].isnumeric():
            game_index = int(received_msg[5:-1])
            if game_index in game_list:
                is_user_attached = server.open(game_list[game_index], user)

        elif received_msg.startswith("Observe(") and received_msg.endswith(")") and received_msg[8:-1].isnumeric():
            game_index = int(received_msg[8:-1])
            if game_index in game_list:
                server.observe(game_list[game_index], user)
                monopoly = game_list[game_index]
                this_thread_is_observer_thread = True
                is_user_attached = True
            else:
                await websocket.send(f"There is no game ({game_index})")
        else:
            await websocket.send(f"Invalid command: {received_msg}")
        if(is_user_attached):
                break

    if this_thread_is_observer_thread:
        await become_observer_thread(monopoly, user)
    else:
        await become_user_thread(monopoly,user)

# Function to handle incoming WebSocket connections
async def handle_websocket(websocket, path):
    # Create a new user for the WebSocket connection
    user = await websocket.recv()

    if server.IfUserInGame(user):
        monopoly=server.user_connection[user]
        become_playing_thread(monopoly,user)
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