# Monopoly
Ersel Hengirmen 2468015  
Mert Başarır 2237063  

We have 4 python files inside `phase2` folder:  
* `User.py` Includes user class
* `Board.py` Includes Board and property classes that are used to play the game
* `Server.py` Includes Server class that are used to implement server functions
* `main.py` Includes main file that is used to host the server.

We also added 3 monopoly board files inside `gameBoards` folder:
* `deneme_in` board file with 4 properties and every cell type included 
* `deneme2_in` board file with lots of chance cards
* `input.json` a bigger board(unchecked)

# How to play
to Host the server with your given port:
```bash
python3 main.py --port {port number}
```
or to use port 3333(default)
```bash
python3 main.py
```


# User steps explained
When a user connects to the server the user will be asked to login or signup.
At this point the user can make 3 actions:
```angular2html
sign up
login
exit
```
After signing up the user will arrive at the lobby screen where games will be presented to the user.
At this point the user can make 4 actions:  
Note: new command is limited to 2-4 players and it will make the user join the game that was created.
```angular2html
New(numberOfPlayers)
Join(gameID)
Observe(gameID)
exit
```
After joining the game users(In addition to normal gameplay actions) and observers will have 2 actions:
```angular2html
list
exit
```
The `list` action will refresh the current state of the game.  
The `exit` action will make them detach from the game and go back to lobby.  
Note: `list` action will only work after the game starts it will not be avaliable in readying phase.