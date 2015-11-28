from __future__ import division
import random
import PredPreyAbility
import PredPreyObject


class PredPreyEngine:
    def __init__(self, world_width=50, world_height=30):
        # Set parameters
        self.squaresize = 20
        self.world_width = world_width
        self.world_height = world_height

        # Create world
        self.world = []

        for y in range(0, world_height):
            for x in range(0, world_width):
                self.world.append('Grass')

        self.maze_generation(0, world_width-1, 0, world_height-1)

        # for y in range(0, world_height):
        #     for x in range(0, world_width):
        #         self.world.append('Grass')
        #
        # for y in range(11,18):
        #     for x in range(21,28):
        #         self.world[y*world_width+x] = 'Water'
        #
        # for y in [3, 27]:
        #     for x in range(3,22):
        #         self.world[y*world_width+x] = 'Brick'
        #     for x in range(27,47):
        #         self.world[y*world_width+x] = 'Brick'
        #
        # for x in [3, 21, 27, 46]:
        #     for y in range(3,7):
        #         self.world[y*world_width+x] = 'Brick'
        #     for y in range(22,27):
        #         self.world[y*world_width+x] = 'Brick'
        #
        # for x in [18, 30]:
        #     for y in range(6,25):
        #         self.world[y*world_width+x] = 'Brick'
        #
        # for x in [6,7,8,9,10,12,13,14,15,16,32,33,34,35,36,38,39,40,42,43]:
        #     for y in range(7,12):
        #         self.world[y*world_width+x] = 'Stone'
        #
        #     for y in range(13,18):
        #         self.world[y*world_width+x] = 'Stone'
        #
        #     for y in range(19,24):
        #         self.world[y*world_width+x] = 'Stone'

        # Create players and data
        self.players = []
        self.objects = []
        self.objects_created = []
        self.objects_removed = []
        self.object_id = 0

        # Simulation data
        self.time = 0
        self.running = True

    def maze_generation(self, left, right, top, bottom):
        if left < right-4 and top < bottom-4:
            x = random.randint(left+2, right-2)
            y = random.randint(top+2, bottom-2)

            for horiz in range(left, right):
                self.world[y*self.world_width + horiz] = 'Brick'
            emptyhoriza, emptyhorizb = random.randint(left+1, x-1), random.randint(x+1, right-1)
            self.world[y*self.world_width + emptyhoriza] = 'Grass'
            self.world[y*self.world_width + emptyhoriza + 1] = 'Grass'
            self.world[y*self.world_width + emptyhorizb] = 'Grass'
            self.world[y*self.world_width + emptyhorizb + 1] = 'Grass'

            for verti in range(top, bottom):
                self.world[verti*self.world_width + x] = 'Brick'
            emptyvertia, emptyvertib = random.randint(top+1, y-1), random.randint(y+1, bottom-1)
            self.world[emptyvertia*self.world_width + x] = 'Grass'
            self.world[(emptyvertia+1)*self.world_width + x] = 'Grass'
            self.world[emptyvertib*self.world_width + x] = 'Grass'
            self.world[(emptyvertib+1)*self.world_width + x] = 'Grass'

            try:
                self.maze_generation(left, x, top, y)
            except:
                None
            try:
                self.maze_generation(x, right, top, y)
            except:
                None
            try:
                self.maze_generation(left, x, y, bottom)
            except:
                None
            try:
                self.maze_generation(x, right, y, bottom)
            except:
                None


    def add_player(self, player_class):
        size = len(self.players)
        player = player_class(size)
        player.alive = True
        self.players.append(player)

    # Used to set action of human controlled player(s)
    def set_action(self, player=0, action=None):
        self.actions[player] = self.interpret_action(player, action)

    # Find a tile not occupied by solid tile or another player
    def random_free_tile(self):
        keep_looking = True
        while keep_looking:
            x = random.randint(0, self.world_width // 2 - 2) * 2
            y = random.randint(0, self.world_height // 2 - 2) * 2

            if not self.tile_unpassable(x,y):
                keep_looking = False
                for player in self.players:
                    try:
                        if player.x == x or player.y == y:
                            keep_looking = True
                            break
                    except:
                        None

        return (x,y)

    # Initiate the engine: All players must be added now
    def init_engine(self):
        # Set data on characters
        for player in self.players:
            player.x, player.y = self.random_free_tile()
            player.direction = 'LEFT'
            player.human = False

        # Initiate the abilities of each player
        self.abilities = []
        for player in self.players:
            temp = []
            for ability in player.abilities:
                temp.append(ability())
            self.abilities.append(temp)

        # TODO Maintain player position, life, cooldown etc. in separate class system? PredPreyPlayerInfo
        # Include self.actions here
        # Make sure there's still a copy of the data in each player class

        # Send world information to both players
        for player in self.players:
            player.world_width = self.world_width
            player.world_height = self.world_height

    # Use to check if simulation is still running or someone won
    def check_running(self):
        if self.running:
            for pred in self.players:
                if pred.type == 'PRED' and pred.alive:
                    for prey in self.players:
                        if prey.type == 'PREY' and prey.alive:
                            if self.collision(pred.x-1, pred.y-1, pred.width+2, pred.height+2, prey.x, prey.y, prey.width, prey.height):
                                prey.alive = False

            self.running = False
            for prey in self.players:
                if prey.type == 'PREY' and prey.alive:
                    self.running = True
                    break

        return self.running

    # Collision detection
    def collision(self, ax, ay, aw, ah, bx, by, bw, bh):
        return (ax+aw > bx and ax < bx+bw and ay+ah > by and ay < by+bh) or (bx+bw > ax and bx < ax+aw and by+bh > ay and by < ay+ah)

    # Interpret action
    def interpret_action(self, index, action=None):
        player = self.players[index]
        if player.alive:
            # Upon receiving action, complete it with a call to appropriate ability
            if action:
                found = False

                for ability in self.abilities[index]:
                    if action[0] == "MOVE" and isinstance(ability, PredPreyAbility.ppa_move):
                        action = ability.use(action[1])
                        found = True
                        break

                    elif action[0] == "TURN" and isinstance(ability, PredPreyAbility.ppa_turn):
                        action = ability.use(action[1])
                        found = True
                        break

                    elif action[0] == "JUMP" and isinstance(ability, PredPreyAbility.ppa_jump):
                        action = ability.use(action[1])
                        found = True
                        break

                    elif action[0] == "FIRE" and isinstance(ability, PredPreyAbility.ppa_weapon):
                        action = ability.use(player.direction)
                        found = True
                        break

                # If player does not have the ability, set to None
                if not found:
                    action = None
        else:
            action = None

        return action


    # Run AI update for all
    def update_ai(self):
        self.actions = []

        for i in range(0, len(self.players)):
            player = self.players[i]
            action = None

            if player.alive and not player.human:
                try:
                    # Send updated simulation data to the player
                    player.update(list(self.players), list(self.objects), list(self.world), list(self.abilities))

                    # Interpret AI action and store it
                    ai_action = player.next()
                    action = self.interpret_action(index=i, action=ai_action)

                except Exception as inst:
                    print("Update and/or AI for player", i, "with error:", inst)

            self.actions.append(action)

    # Returns True if the tile cannot be passed through
    def tile_solid(self, x, y):
        index = y * self.world_width + x
        if index < 0 or index >= self.world_width * self.world_height:
            return False
        else:
            tile = self.world[index]
            return (tile == 'Brick' or tile == 'Stone')

    def tile_unpassable(self, x, y):
        index = y * self.world_width + x
        if index < 0 or index >= self.world_width * self.world_height:
            return False
        else:
            tile = self.world[index]
            return (tile == 'Water') or self.tile_solid(x, y)

    # Update, create, destroy any objects in the world
    def handle_objects(self):
        self.objects_removed = []
        self.objects_created = []

        # Create new?
        for object_type in [PredPreyObject.ppo_projectile]:
            if object_type.creation_probability > random.uniform(0,1):
                # Specific creation in terms of type

                self.object_id += 1
                object.id = self.object_id
                self.objects.append(object)
                self.objects_created.append(object.id)

        # Send update to those that exist
        for object in self.objects:
            action = object.update()
            object.action = action

            if action:
                if action[0] == "DESTROY":
                    self.objects_removed.append(object.id)
                    self.objects.remove(object)
                    continue

                elif action[0] == "MOVE":
                    px = object.x
                    py = object.y
                    cont = True
                    for i in range(1, action[2] + 1):
                        if not cont:
                            break

                        if action[1] == 'UP':
                            py -= 1
                        elif action[1] == 'DOWN':
                            py += 1
                        elif action[1] == 'LEFT':
                            px -= 1
                        elif action[1] == 'RIGHT':
                            px += 1

                        if self.tile_solid(px, py):
                            self.objects_removed.append(object.id)
                            self.objects.remove(object)
                            break

                        if action:
                            for player in self.players:
                                if self.collision(px, py, object.width, object.height, player.x, player.y, player.width, player.height) and player.alive:
                                    if isinstance(object, PredPreyObject.ppo_projectile):
                                        collision_action = object.use()
                                        print("col_action =",collision_action)
                                        if collision_action[0] == 'KILL':
                                            player.alive = False
                                            self.objects_removed.append(object.id)
                                            self.objects.remove(object)
                                            cont = False
                                            break
                        if action:
                            object.x = px
                            object.y = py
                            object.action = action

            if object.x < 0 or object.x > self.world_width or object.y < 0 or object.y > self.world_height:
                self.objects_removed.append(object.id)
                self.objects.remove(object)
                break

    # Tick to next step (if human control, assume already submitted)
    def next(self):
        # Advance time
        self.time += 1

        # Send update to every ability - handles cooldown and other stuff
        for player_list in self.abilities:
            for ability in player_list:
                ability.update()

        # Send update to every object
        self.handle_objects()

        # Make sure action is valid, otherwise set to None
        # World limit
        for i in range(0, len(self.players)):
            player = self.players[i]
            action = self.actions[i]
            if action:
                if not player.alive:
                    action = None

                # elif (action[0] == 'MOVE' and player.type == 'PRED'):
                #     if (action[1] == 'UP' and player.direction == 'DOWN') or (action[1] == 'DOWN' and player.direction == 'UP') or (action[1] == 'LEFT' and player.direction == 'RIGHT') or (action[1] == 'RIGHT' and player.direction == 'LEFT'):
                #         action = None

                elif (action[0] == 'TURN'):
                    None  # Turning is always allowed

                elif action[0] == 'JUMP' or action[0] == 'MOVE':
                    px = player.x
                    py = player.y
                    cont = True

                    for i in range(1, action[2] + 1):
                        if not cont:
                            break

                        if action[1] == 'UP':
                            py -= 1
                        elif action[1] == 'DOWN':
                            py += 1
                        elif action[1] == 'LEFT':
                            px -= 1
                        elif action[1] == 'RIGHT':
                            px += 1

                        if (py < action[2] - 1 and action[1] == 'UP') or (py > self.world_height - player.height - action[2] + 1 and action[1] == 'DOWN') or (px < action[2] - 1 and action[1] == 'LEFT') or (px > self.world_width - player.width - action[2] + 1 and action[1] == 'RIGHT'):
                            action[2] = i-1
                            cont = False

                        if self.tile_unpassable(px, py) and cont:
                            action[2] = i-1
                            cont = False

                        for other in self.players:
                            if other.x != player.x or other.y != player.y:
                                if self.collision(px, py, player.width, player.height, other.x, other.y, other.width, other.height) and other.alive and cont:
                                    action[2] = i-1
                                    cont = False
                                    break

        # Execute movement command
        for i in range(0, len(self.players)):
            player = self.players[i]
            action = self.actions[i]
            if action:
                if action[0] == 'MOVE' or action[0] == 'JUMP':
                    player.direction = action[1]

                    if action[1] == 'UP':
                        player.y -= action[2]
                    elif action[1] == 'DOWN':
                        player.y += action[2]
                    elif action[1] == 'LEFT':
                        player.x -= action[2]
                    elif action[1] == 'RIGHT':
                        player.x += action[2]

                elif action[0] == 'TURN':
                    player.direction = action[1]

        # Execute fire commands
        for i in range(0, len(self.players)):
            player = self.players[i]
            action = self.actions[i]
            if action:
                if action[0] == 'FIRE':
                    if action[1] == 'UP':
                        projectile = PredPreyObject.ppo_projectile(player.x, player.y - 1, action[1])
                    elif action[1] == 'DOWN':
                        projectile = PredPreyObject.ppo_projectile(player.x, player.y + 1, action[1])
                    elif action[1] == 'LEFT':
                        projectile = PredPreyObject.ppo_projectile(player.x - 1, player.y, action[1])
                    elif action[1] == 'RIGHT':
                        projectile = PredPreyObject.ppo_projectile(player.x + 1, player.y, action[1])

                    self.object_id += 1
                    projectile.id = self.object_id
                    self.objects.append(projectile)
                    self.objects_created.append(projectile.id)

        # Send commands along for GUI update
        GUI_actions = []
        for i in range(0, len(self.players)):
            action = self.actions[i]
            GUI_actions.append(action)
        return GUI_actions
