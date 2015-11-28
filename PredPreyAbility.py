# TEMPLATE CLASS FOR ADDING ABILITIES
class ppa_template:
    # Return True if ability is ready to use, False otherwise
    def can_use(self):
        None

    # If can be used, return appropriate Action. Otherwise None
    def use(self):
        None

    # Called once every time step. Use to reduce cooldown.
    def update(self):
        None


# Typical movement
class ppa_move:
    def __init__(self):
        self.movespeed = 1

    def use(self, direction):
        if direction in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
            return ["MOVE", direction, self.movespeed]

    def update(self):
        None

# Typical turn
class ppa_turn:
    def __init__(self):
        None

    def use(self, direction):
        if direction in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
            return ["TURN", direction]

    def update(self):
        None

# Typical jump of four steps
class ppa_jump:
    def __init__(self):
        self.cooldown = 0
        self.jumpspeed = 3

    def can_use(self):
        return self.cooldown == 0

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1

    def use(self, direction):
        if self.cooldown == 0:
            self.cooldown = 6
            return ["JUMP", direction, self.jumpspeed]
        else:
            return None


# Classic weapon with 1-projectile
class ppa_weapon:
    def __init__(self):
        self.cooldown = 0

    def can_use(self):
        return self.cooldown == 0

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1

    def use(self, direction):
        if self.cooldown == 0:
            self.cooldown = 10
            return ["FIRE", direction]
        else:
            return None
