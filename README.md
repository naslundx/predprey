# predprey
An AI simulation engine written in Python3.

# old comments
To run, start Game.py with Python

GAME CONTROLS
=============
Restart: W
4x faster speed: Q (hold)
Play/Pause: Z

M: Select player up
N: Select player down

To steer a player, use M and N to select a player (its name will be coloured yellow).

Up / Down / Left / Right arrow key: Choose direction.
Default choice is to move
Holding A means firing weapon (in current direction) - if possible
Holding S means jumping (in the chosen direction) - if possible

ADDING/SUBTRACTING PLAYERS
==========================
In game.py, at the bottom under

def main():

Change the number of calls to pp_engine.add_player(...) to have more/fewer Pred/Prey.
