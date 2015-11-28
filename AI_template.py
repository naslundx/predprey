import random
import math
from PredPreyAbility import ppa_move, ppa_jump, ppa_weapon

class Pred:
    # Constructor. Make sure to set width, height, type ("PREY" or "PRED"),
    # me (this instance's ID), and a list of abilities found in PredPreyAbility.
    def __init__(self, me):
        self.width = 1
        self.height = 1
        self.type = "PRED"
        self.me = me
        self.abilities = [ppa_move, ppa_jump, ppa_weapon]

    # Be sure to save the size of the world: world_width and world_height,
    # to have some idea of anything
    # Deprecate - move to constructor?
    def setup(self, world_width, world_height):
        self.world_width = world_width
        self.world_height = world_height

    # This method is called on every time step. Use this to save updated data,
    # and if needed to some processing.
    #
    # players - List of all players and their data
    # projectiles - List of all projectiles (will be replaced by objects in general later on)
    # world - A list of every tile in the world
    # abilities - A list of every ability for every player
    def update(self, players, objects, world, abilities):
        # All players are stored in self.players.
        # The current player is self.players[self.me]
        # It has important data, such as coordinates (.x and .y)
        # and size (.width and .height) and also type (.type) which is "PRED"
        # or "PREY"
        self.players = players

        # All current objects (if any) are stored in self.projectiles
        # An example to check if a projectile is at coordinates (x,y):
        # for object in self.objects:
        #   if isinstance(object, PredPreyObject.ppo_projectile):
        #       if projectile.x == x and projectile.y == y:
        #           ...
        self.objects = objects

        # Your abilities (such as move, jump, fire) are in self.abilities.
        # The list self.abilities[self.me] is the list of your abilities.
        # An example to check if you can fire your weapon:
        #
        # for ability in self.abilities[index]:
        #   if isinstance(ability, PredPreyAbility.ppa_weapon):
        #       if ability.can_use():
        #           ...
        self.abilities = abilities

        # The world is stored as a list in self.world. For example self.world[y * self.world_width + x] is the tile on position (x,y).
        # It is a string, and if it's "BRICK", "STONE" or "WATER", you cannot pass through it.
        self.world = world

    # This is where the AI is, perform any computations and return an appropriate
    # action. Must return something. If doing nothing, return None.
    def next(self):
        return None

        # Possible returns are:
        # ["MOVE", "UP"]
        # ["JUMP", "UP"]
        # ["FIRE"] (fire is performed in your current direction)
