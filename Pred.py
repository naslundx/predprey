from PredPreyAbility import ppa_move, ppa_jump, ppa_weapon
import PredPreyObject
# Queues.PriorityQueue is also useful when parallelism is used 
try:
    import Queue as Queue # version 2.x
except:
    import queue as Queue # version 3.x
#import collections
import sys

class Pred:
    def __init__(self, me):
        self.width = 1
        self.height = 1
        self.type = "PRED"
        self.gfx = "PredHeadTransparent"
        self.me = me
        self.abilities = [ppa_move, ppa_jump, ppa_weapon]
        self.human = False

    # Input data about world and initial location
    def setup(self, world_width, world_height):
        self.alive = True
        self.world_width = world_width
        self.world_height = world_height

    # Update location and world
    def update(self, players, projectiles, world, abilities):
        self.players = players
        self.projectiles = projectiles
        self.abilities = abilities
        self.world = world

    ########################### Methods #######################

    # Conveting 2D lists to 1D list
    def pos2DTopos1D(self, x, y):
        return y * self.world_width + x

    # Checking borders if it is inside the world
    def checkBorder(self, point):
        if point >= 0 and point < self.world_width * self.world_height: return True
        else: return False

    # 1D array problem: next index is on the other side of
    # the world (left and right in this case,the down
    # and up are not important as their index numbers are not next to
    # each other)
    def checkPointJump(self, current, points):
        if current // self.world_width  != points[1] // self.world_width: points.remove(points[1])
        if current // self.world_width  != points[0] // self.world_width: points.remove(points[0])
        return points

    # Getting "Projectile tiles"
    def getProjectTiles(self):
        projectilesPos= set()
        for object in self.projectiles:
            if isinstance(object, PredPreyObject.ppo_projectile):
                px = object.x
                py = object.y
                pos = self.pos2DTopos1D(px, py)
                projectile_speed = PredPreyObject.ppo_projectile.speed

                # Get the set on the way of the projectile
                for i in range(1, 2 * projectile_speed + 1):
                    if object.direction == 'UP': 
                        projectilesPos.add(pos - i * self.world_width)
                    elif object.direction == 'DOWN': 
                        projectilesPos.add(pos + i * self.world_width)
                    elif object.direction == 'LEFT': 
                        projectilesPos.add(pos - i)
                    elif object.direction == 'RIGHT': 
                        projectilesPos.add(pos + i)
        return projectilesPos

    # NO WATER; BRICK; STONE + Pred Positions + Projectile tiles
    def checkPassable(self, index, value):
        predNoL = index not in self.predPoses # for sights
        projectileNoL = index not in self.projectTiles 
        tileNoL = (value != "Water" and value != "Brick" and value != "Stone")
        return projectileNoL and tileNoL and predNoL

    # Get Neighbours (isn't it obvious?)
    def getNeighbours(self, index):
        candidates = [index + 1, index - 1, index - self.world_width, index + self.world_width]
        candidates = set(self.checkPointJump(index, candidates))
        # To get invalid values first
        valuesToRemove = set()
        #for each in candidates:
        for next in candidates:
            if not self.checkBorder(next): valuesToRemove.add(next)
            elif not self.checkPassable(next, self.world[next]): valuesToRemove.add(next);

        candidates -= valuesToRemove # Set Minus
        return candidates

    # Manhattan distance on a grid
    def heuristic(self, a, b):
        return abs((a // self.world_width) - (b // self.world_width)) \
             + abs((a % self.world_width) - (b % self.world_width))

    # List back the path
    def reconstructPath(self, came_from, current):
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.append(current)
        total_path.reverse()
        return total_path

    # The famous A*, it should find path unless it is impossible
    def AStar(self, start, end):
        closedset = []
        openset = [start]
        came_from = {}

        g_score = {}; 
        f_score = {}
        #f_score = Queue.PriorityQueue()
        g_score[start] = 0
        f_score[start] = g_score[start] + self.heuristic(start, end)
        #f_score.put((g_score[start] + self.heuristic(start, end), start))

        # Until the openset is empty
        while openset:
            # Find the minimum f_score amongst openset
            mi = self.maxHeuristicValue
            index = None
            for next in openset:
                if f_score[next] < mi:
                    mi = f_score[next]
                    index = next
            current = index
            #current = f_score.get(0)[1]
            #print("start = ", start)
            #print("current =", current)
            #print("openset =", openset)

            # If the current is the goal, finish it
            if current == end:
                return self.reconstructPath(came_from, end)

            #try:
            openset.remove(current)
            #except:
            #    print("Error in openset")
            closedset.append(current)

            for next in self.getNeighbours(current):
                # Check if it already visited, they are listed in the closeset
                if next not in closedset:
                    try:
                        tentative_g_score = g_score[current] + self.penalty[current] # close to other preds
                    except:
                        tentative_g_score = g_score[current] + 1 # neighbour distance
                    if next not in openset: # Discovered new tile
                        openset.append(next)
                        came_from[next] = current
                        g_score[next] = tentative_g_score
                        f_score[next] = g_score[next] + self.heuristic(next, end)
                        #f_score.put((g_score[next] + self.heuristic(next, end), next))
                    else: # It is in the list but not visited yet
                        if tentative_g_score < g_score[next]: # if we have less score, update the current results
                            came_from[next] = current
                            g_score[next] = tentative_g_score
                            f_score[next] = g_score[next] + self.heuristic(next, end)
                            #f_score.put((g_score[next] + self.heuristic(next, end), next))
        print("WARNING: A* SEARCH PATH GIVES NONE PRED.PY")
        return None

    # Move in the game
    def direc(self, pos1, pos2):
        if pos2 == (pos1 + self.world_width): return "DOWN"
        elif pos2 == (pos1 - self.world_width): return "UP"
        elif pos2 == (pos1 + 1): return "RIGHT"
        elif pos2 == (pos1 - 1): return "LEFT"
        else: print("ERROR IN DIRECTIONS (PRED.PY)")

    # Jump or Fire (turn is also available)
    def chooseAbility(self, command):
        for ability in self.abilities[self.me]:
            if isinstance(ability, command):
                return ability
        return None

    # Create the straight line until not-passable tile
    def getLineList(self, start, end, step):
        arr = set()
        current = start
        # LEFT and UP
        if start > end:
            while current > end:
                current -= step
                if current <= end: break # Border
                if self.checkPassable(current, self.world[current]):
                    arr.add(current)
                else: break # Reached not-passable tile
        # RIGHT and DOWN
        else:
            while current < end:
                current += step
                if current >= end: break # Border
                if self.checkPassable(current, self.world[current]):
                    arr.add(current)
                else: break # Reached not-passable tile
        return arr

    # Get the list depending on the current direction of the Prey
    def lineDirection(self, pos1, pos2, face):
        if face == "DOWN":
            line = self.getLineList(pos1, self.world_width * self.world_height, self.world_width)
        elif face == "UP":
            line = self.getLineList(pos1, (pos1 % self.world_width) - self.world_width, self.world_width)
        elif face == "RIGHT":
            line = self.getLineList(pos1, ((pos1 // self.world_width) + 1) * self.world_width , 1)
        elif face == "LEFT":
            line = self.getLineList(pos1, (pos1 // self.world_width) * self.world_width - 1, 1)
        else:
            print("ERROR IN LINEDIRECTION PRED.PY")
        return line

    # Get the list of all directions of the Prey
    def fourLineDirections(self, pos1, pos2):
        allList = set([pos1])
        allList.update(self.lineDirection(pos1, pos2, "DOWN"))
        allList.update(self.lineDirection(pos1, pos2, "UP"))
        allList.update(self.lineDirection(pos1, pos2, "RIGHT"))
        allList.update(self.lineDirection(pos1, pos2, "LEFT"))
        return allList

    # Choose the closest prey
    def chooseClosestPrey(self, predPos, preyPoses):
        mi = self.maxHeuristicValue
        chosen = None
        for next in preyPoses:
            try:
                target = len(self.AStar(predPos, next)) # TODO: WARNING: PERFORMANCE CONSUMING
            except:
                target = self.maxHeuristicValue # not reachable
            if target < mi:
                mi = target
                chosen = next
        return chosen

    # Limiting the distance in one direction
    def straightN(self, path, see, Nrange):
        size = len(path)
        if size >= Nrange[0] and size <= Nrange[1] and see: return True
        return False

    def getDiamondTiles(self, pos, n, pen):
        self.penalty = {} # Load to the class
        for i in range(n):
            for j in range(n-i):
                try:
                    self.penalty[pos + i + self.world_width * j] += (n - (abs(i) + abs(j))) * pen
                    self.penalty[pos - i + self.world_width * j] += (n - (abs(i) + abs(j))) * pen
                    self.penalty[pos + i - self.world_width * j] += (n - (abs(i) + abs(j))) * pen
                    self.penalty[pos - i - self.world_width * j] += (n - (abs(i) + abs(j))) * pen
                except: 
                    self.penalty[pos + i + self.world_width * j] = (n - (abs(i) + abs(j))) * pen
                    self.penalty[pos - i + self.world_width * j] = (n - (abs(i) + abs(j))) * pen
                    self.penalty[pos + i - self.world_width * j] = (n - (abs(i) + abs(j))) * pen
                    self.penalty[pos - i - self.world_width * j] = (n - (abs(i) + abs(j))) * pen

    def generatePenaltyTiles(self, predPos, predPoses):
        backup = list(predPoses) # Safety in code
        backup.remove(predPos) 
        for next in backup:
            self.getDiamondTiles(next, 10 , 5) # Might need some calibration here

    ########################### Methods #######################

    ########## THE MAIN PART ##############
    def next(self):
        # So-called maximum heuristic value in the map
        self.maxHeuristicValue = self.world_width * self.world_height 

        # Get Projectile tiles if there is at least one
        self.projectTiles = self.getProjectTiles()

        # Read the players
        currentPred = self.pos2DTopos1D(self.players[self.me].x, self.players[self.me].y)
        allPreyPoses = []
        allPredPoses = []
        samePredPoses = []
        for player in self.players:
            if player.type == 'PREY' and player.alive:
                allPreyPoses.append(self.pos2DTopos1D(player.x, player.y))
            elif player.type == 'PRED' and player.alive:
                pos1D = self.pos2DTopos1D(player.x, player.y)
                if pos1D in allPredPoses: # gets the second or more player that is on the same postion
                    samePredPoses.append(player)
                allPredPoses.append(pos1D)

        # Separate the preds if they happened to be at the same
        # position
        if samePredPoses:
            for next in samePredPoses:
                if next == self.players[self.me]:
                    return None

        # Treat Preds as not-passable tiles for sights
        self.predPoses = allPredPoses

        # Penalise this pred for going next to other preds
        self.generatePenaltyTiles(currentPred, allPredPoses)

        # Choose the closest prey for this pred
        chosenPrey = allPreyPoses[0]
        if len(allPreyPoses) > 1: chosenPrey = self.chooseClosestPrey(currentPred, allPreyPoses)

        # Get the shortest path
        shortestPath = self.AStar(currentPred, chosenPrey)
        
        if shortestPath != None:
            # See sight of the prey
            sight = self.lineDirection(currentPred, chosenPrey, self.direction)

            # All possible sights of the prey
            allSight = self.fourLineDirections(currentPred, chosenPrey)

            # Prey goes ... 
            way = self.direc(shortestPath[0], shortestPath[1])

            # Abilities
            jump_ability = self.chooseAbility(ppa_jump)
            fire_ability = self.chooseAbility(ppa_weapon)

            # Logic: Sees sight and all sights or not
            inSightL = chosenPrey in sight
            allInSightL = chosenPrey in allSight

            # Logic: jumps in the right path or not
            jumpPathL = set(shortestPath[:4]).issubset(allSight)

            # Logic: Catch it now or catch up
            catchL = self.straightN(shortestPath, allInSightL, (2,5)) 
            catchupL = self.straightN(shortestPath, True, (11, self.maxHeuristicValue)) # True means the sight doesn't matter

            #Logic: Projectile goes with 2, put some pressure
            putPresL = self.straightN(shortestPath, inSightL, (6,10))

            # Control Check for move
            # Default move
            move = ["MOVE", way]
            if jump_ability.can_use() and (catchL or catchupL):               
                if jumpPathL or catchL:
                    move = ["JUMP", way]
            elif fire_ability.can_use() and putPresL:
                move = ["FIRE", self.direction]
            return move
        else:
            # Possibilities
            # 1) There is no way to reach prey(s)
            # 2) There is only one prey and there is a projectile going toward it,
            # the preds will not risk their lives
            print("Returns None PREDS")
            return None
