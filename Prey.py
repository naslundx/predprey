from __future__ import division
import random
import math
from PredPreyAbility import ppa_move
import PredPreyObject
import sys


class Prey:
    def __init__(self, me):
        self.width = 1
        self.height = 1
        self.type = "PREY"
        self.gfx = "PreyTransparent"
        self.abilities = [ppa_move]
        self.me = me

    # Update location and world
    def update(self, players, objects, world, abilities):
        self.players = players
        self.objects = objects
        self.world = world
        self.abilities = abilities


    # This is where the AI is
    def next(self):
        # === Store my position
        prey_pos = self.pos2DTopos1D(self.players[self.me].x, self.players[self.me].y)

        # === Calculate the safety score for each position ===
        # Setup list, init to zero
        self.safety_score = []
        for y in range(0, self.world_height):
            for x in range(0, self.world_width):
                self.safety_score.append(0)

        # Set minimal score (-999999) to tiles not passable
        for y in range(0, self.world_height):
            for x in range(0, self.world_width):
                pos = self.pos2DTopos1D(x,y)
                if not self.checkPassable(self.world[pos]):
                    self.safety_score[pos] = -99

        # For each Pred...
        #suicide_distance = 7
        for player in self.players:
            if player.type == 'PRED' and player.alive:
                visited, queue = set(), [(self.pos2DTopos1D(player.x, player.y), 0)]
                while queue:
                    vertex = queue.pop(0)
                    if vertex[0] not in visited:
                        visited.add(vertex[0])
                        #if vertex[1] <= suicide_distance:
                        #    self.safety_score[vertex[0]] = -99
                        #else:
                        self.safety_score[vertex[0]] += vertex[1]
                        neighbours = self.getNeighbours(vertex[0])

                        for n in neighbours:
                            if n not in visited:
                                queue.append((n, vertex[1] + 1))

        # For each projectile...
        for object in self.objects:
            if isinstance(object, PredPreyObject.ppo_projectile):
                px = object.x
                py = object.y
                steps = 0

                while steps < PredPreyObject.ppo_projectile.speed * 3:
                    pos = self.pos2DTopos1D(px,py)

                    # Check if (px,py) is outside
                    if px < 0 or px >= self.world_width or py < 0 or py >= self.world_height:
                        # TODO Also check if it collided with something
                        break

                    # Set safety very low
                    self.safety_score[pos] = -30
                    # TODO For some reason this doesn't seem to work

                    # Move along
                    if object.direction == 'UP':
                        py -= 1
                    elif object.direction == 'DOWN':
                        py += 1
                    elif object.direction == 'LEFT':
                        px -= 1
                    elif object.direction == 'RIGHT':
                        px += 1

                    steps += 1


        # For each Prey... (If there are more than 1 we don't want them to group together)
        for player in self.players:
            if player.type == 'PREY' and self.pos2DTopos1D(player.x, player.y) != prey_pos and player.alive:

                visited, queue = set(), [(self.pos2DTopos1D(player.x, player.y), 20)]
                while queue:
                    vertex = queue.pop(0)
                    if vertex[0] not in visited and vertex[1] > 0:
                        visited.add(vertex[0])
                        self.safety_score[vertex[0]] -= vertex[1]
                        neighbours = self.getNeighbours(vertex[0])

                        for n in neighbours:
                            if n not in visited:
                                queue.append((n, vertex[1] - 1))

        # === Find the point with maximum safety score (X,Y)
        safest_point = 0
        for y in range(1, self.world_height-1, 2):
            for x in range(1, self.world_width-1, 2):
                pos = self.pos2DTopos1D(x,y)
                score = self.safety_score[pos]
                #print "(%d,%d)=%d" % (x,y,score)
                if score > self.safety_score[safest_point]:
                    safest_point = pos

        # === Find the A* path from (self.x, self.y) to (X,Y)
        # Only consider a path with a certain minimal safety
        # If no path can be found, iterate with a lower limit until found
        path = None
        testing_minimal_safety = 20
        while not path:
            testing_minimal_safety -= 2
            path = self.AStar(prey_pos, safest_point, self.objects, testing_minimal_safety)
            print testing_minimal_safety


        # === Return the movement to get on that path
        if path:
            return ["MOVE", self.find_direction(path[0], path[1])]
        else:
            return None





    # ________ FOLLOWING CODE IS STOLEN (HEHEHEHE) AND SLIGHTLY MODIFIED FROM DENIZ PRED.PY CODE ___________

    ########################### Methods #######################

    # Conveting 2D lists to 1D list
    def pos2DTopos1D(self, x ,y):
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

    # NO WATER; BRICK; STONE
    def checkPassable(self, value):
        return (value != "Water" and value != "Brick" and value != "Stone")

    # Get Neighbours (isn't it obvious?)
    def getNeighbours(self, index, minimal_safety=-999):
        candidates = [index + 1, index - 1, index - self.world_width, index + self.world_width]
        candidates = set(self.checkPointJump(index, candidates))
        # To get invalid values first
        valuesToRemove = set()
        #for each in candidates:
        for next in candidates:
            if not self.checkBorder(next):
                valuesToRemove.add(next)
            elif not self.checkPassable(self.world[next]):
                valuesToRemove.add(next);
            elif minimal_safety > -50:
                if self.safety_score[next] < minimal_safety:
                        valuesToRemove.add(next)
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
    def AStar(self, start, end, projectiles, minimal_safety=-99999):
        closedset = []
        openset = [start]
        came_from = {}

        g_score = {}; f_score = {}
        g_score[start] = 0
        f_score[start] = g_score[start] + self.heuristic(start, end)

        # Until the openset is empty
        while openset:
            # Find the minimum f_score amongst openset
            mi = self.world_width * self.world_height
            index = None
            for next in openset:
                if f_score[next] < mi:
                    mi = f_score[next]
                    index = next
            current = index

            # If the current is the goal, finish it
            if current == end:
                return self.reconstructPath(came_from, end)

            openset.remove(current)
            closedset.append(current)

            for next in self.getNeighbours(current, minimal_safety):
                # Check if it already visited, they are listed in the closeset
                if next not in closedset:
                    tentative_g_score = g_score[current] + 1 # neighbour distance
                    if next not in openset: # Discovered new tile
                        openset.append(next)
                        came_from[next] = current
                        g_score[next] = tentative_g_score
                        f_score[next] = g_score[next] + self.heuristic(next, end)
                    else: # It is in the list but not visited yet
                        if tentative_g_score < g_score[next]: # if we have less score, update the current results
                            came_from[next] = current
                            g_score[next] = tentative_g_score
                            f_score[next] = g_score[next] + self.heuristic(next, end)
        return None

    def find_direction(self, pos1, pos2):
        if pos2 == (pos1 + self.world_width):
            return "DOWN"
        elif pos2 == (pos1 - self.world_width):
            return "UP"
        elif pos2 == (pos1 + 1):
            return "RIGHT"
        else:
            return "LEFT"
