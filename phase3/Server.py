from Board import Board

from threading import Lock

#-------------------------------------------------------------------------------------
'''

In class library phase you should implement your basic classes and write a command
line test application demonstrating all features of your library.

'''
#-------------------------------------------------------------------------------------

class Server:
    game_board_filename = "../gameBoards/deneme_in"

    def __init__(self):
        self.monopoly_instances = {}
        self.monopoly_list_mutex = Lock()
        self.new_game_id=0

    def new(self,number_of_users=2):
        if(number_of_users>4 or number_of_users<2):
            return None
        with self.monopoly_list_mutex:
            self.new_game_id+=1
            monopoly = Board(self.game_board_filename, number_of_users)
            self.monopoly_instances[self.new_game_id]=monopoly
        return monopoly
    def list(self): # TODO control maybe a copy of the list can be send instead(copied in mutex)
        return self.monopoly_instances
    def observe(self,game,user): # returns true or false
        with self.monopoly_list_mutex:
            game.attach_observer(user)
    def observe_with_ID(self,ID,user): # returns true or false
        with self.monopoly_list_mutex:
            if ID in self.monopoly_instances:
                self.monopoly_instances[ID].attach_observer(user)
                return True
            else:
                return False
            game.attach_observer(user)
    def open(self,game,user): # returns true or false
        with self.monopoly_list_mutex:
            is_user_attached=game.attach(user)
        return is_user_attached
    def open_with_ID(self,ID,user): # returns true or false
        with self.monopoly_list_mutex:
            if ID in self.monopoly_instances:
                is_user_attached=self.monopoly_instances[ID].attach(user)
                return is_user_attached
            else:
                return False
    def close(self,game,user): # TODO
        if game.WaitingState==True:
            game.removeUser(user)
        else:
            game.detach(user)

    def game_is_over(self, game_index):
        del self.monopoly_instances[game_index]
