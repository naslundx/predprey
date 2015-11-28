# TEMPLATE CLASS FOR ADDING OBJECTS
class ppo_template:
    # Specify the probability of an instance being created at any time step
    creation_probability = 0.01
    solid = True

    # Constructor, set any instance-specific variables here
    def __init__(self):
        self.gfx = "filename.gif"
        self.type = "TEMPLATE"

    # Called once every time step. Use to update timer if temporary etc.
    # If you want it destroyed, return ["DESTROY"]
    def update(self):
        None

    # Called when a player interacts (touches) an object
    # For projectiles: Return ["KILL"]
    def use(self):
        return None


# Projectile
class ppo_projectile:
    creation_probability = 0
    gfx = "Projectile"
    solid = True
    speed = 2

    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.width = 1
        self.height = 1
        self.direction = direction
        self.action = []

    def update(self):
        return ["MOVE", self.direction, ppo_projectile.speed]

    def use(self):
        return ["KILL"]

# Teleporter
# class ppo_teleporter:
#     creation_probability = 0.5
#     gfx = "TELEPORTER"
#
#     def __init__(self):
#         ppo_teleporter.creation_probability = 0  # Only allow 1 instance at a time
#         self.lifetime = 100
#
#     def update(self):
#         self.lifetime -= 1
#         if self.lifetime <= 0:
#             return ["DESTROY"]
#         return None
#
#     def use(self, player):
#         if player.type == 'PRED':
#             return ["TELEPORT", 10, 1]
#
#         return None
