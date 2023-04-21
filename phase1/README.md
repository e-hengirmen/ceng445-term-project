# Monopoly
Ersel Hengirmen 2468015  
Mert Başarır 2237063  

We have 3 python files:  
* `User.py` Includes user class
* `Board.py` Includes Board and property classes that are used to play the game
* `demo.py` Includes demo file that is used to play the game **FOR A PREPLAYED GAME(use deneme_in)**
* `main.py` Includes main file that is used to play the game **FOR A NORMAL GAME**

We also added 3 monopoly board files:
* `deneme_in` board file with 4 properties and every cell type included 
* `deneme2_in` board file with lots of chance cards
* `input.json` a bigger board(unchecked)

# How to play
to play the preplayed demo game:
```bash
python3 demo.py <{board_file}
```
to play the the game turn by turn:
```bash
python3 main.py <{board_file}
```