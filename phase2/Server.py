from Board import Board
from User import User

from threading import Lock

#-------------------------------------------------------------------------------------
'''

In class library phase you should implement your basic classes and write a command
line test application demonstrating all features of your library.

'''
#-------------------------------------------------------------------------------------

class Server:
    game_board_filename = "../gameBoards/input.json"

    def __init__(self):
        self.monopoly_instances = {}
        self.monopoly_list_mutex = Lock()
        self.new_game_id=0

    def new(self,number_of_users=2):
        if(number_of_users>4 or number_of_users<2):
            return None
        with self.monopoly_list_mutex:
            self.new_game_id+=1
            monopoly = Board(self.game_board_filename, self, self.new_game_id,number_of_users)
            self.monopoly_instances[self.new_game_id]=monopoly
        return monopoly
    def list(self): # TODO control maybe a copy of the list can be send instead(copied in mutex)
        return self.monopoly_instances
    def observe(self,game,user): # returns true or false
        with self.monopoly_list_mutex:
            game.attach_observer(user, user.callback)
    def open(self,game,user): # returns true or false
        with self.monopoly_list_mutex:
            is_user_attached=game.attach(user, user.callback, user.turncb)
        return is_user_attached
    def close(self,game,user): # TODO
        game.removeUser(user)

    def game_is_over(self, game_index):
        del self.monopoly_instances[game_index]
