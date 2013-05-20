# -*- coding: utf8 -*-

"""
    astar.py - A* algorithm implementation
"""

from math import sqrt
import scipy
import scipy.signal

class Cell(object):

    def __init__(self, x, y, reachable=True):
        self.reachable = reachable
        self.x = int(x)
        self.y = int(y)
        self.parent = None

        # Cost to move to an adjacent cell
        self.g = 0

        # Estimated distance to the goal (Manhattan distance)
        self.h = 0

        # Total "score" : h + g
        self.f = 0

    def __eq__(self, cell):
        return self.x == cell.x and self.y == cell.y and self.reachable == cell.reachable

    def distance(self, cell):
        return sqrt((self.x - cell.x)**2 + (self.y - cell.y)**2)

    def heuristicDistance(self, cell):
        return self.diagonalDistance(cell)

    def manhattanDistance(self, cell):
        return abs(self.x - cell.x) + abs(self.y - cell.y)

    def diagonalDistance(self, cell):

        xDist = abs(self.x - cell.x)
        yDist = abs(self.y - cell.y)

        if xDist > yDist:
            return 1.4 * yDist + (xDist - yDist)
        else:
            return 1.4 * xDist + (yDist - xDist)

    def path(self):
        """ Returns the path that led to this cell """
        resPath = [self]
        cell = self
        while cell.parent != None:
            resPath.append(cell.parent)
            cell = cell.parent

        # Returning the reversed list (as resPath goes bottom-up)
        return resPath[::-1]

    def __str__(self):
        """ String representation,  for debugging only """

        return "Cell [{}, {}] | Reachable : {}".format(self.x, self.y, self.reachable)


class DiscreteMap:

    def __init__(self, svgMap, division=5, radius=100):

        self.division = division

        self.width = int(svgMap.width/division)
        self.height = int(svgMap.height/division)
        self.division = division

        # Open and closed list, used for A* algorithm
        self.ol = set()
        self.cl = set()

        self.svgMap = svgMap

        # The initial grid (only taking into account the shapes, not their perimeter)
        self.initgrid = [[Cell(x, y) for x in xrange(self.width)] for y in xrange(self.height)]

        # The grid that'll take into account the shapes' 'perimeter' (to avoid collisions with the car)
        self.grid = [[Cell(x, y) for x in xrange(self.width)] for y in xrange(self.height)]

        for y in xrange(self.height):
            for x in xrange(self.width):
                # The cell (x, y) will represent the point ( (x + 0.5)*division, (y + 0.5)*division )
                xi, yi = (x + 0.5)*self.division, (y + 0.5)*self.division
                obstacle = self.svgMap.isObstacle(xi, yi)
                self.initgrid[y][x].reachable = not obstacle
                self.grid[y][x].reachable = not obstacle

        self.setRadius(radius)

    def setRadius(self, radius):
        """ Sets as unreachable the cells that have an obstacle in a certain radius """
        r = radius / self. division
        # Avoiding nil radiuses
        r = max(1, r)
        
        # 1 : Unreachable ; 0 : Reachable
        car = scipy.array([[1 for i in xrange(r)] for j in xrange(r)])
        grid = scipy.array([[0 if self.initgrid[i][j].reachable else 1 for j in xrange(
            self.width)] for i in xrange(self.height)])

        result = scipy.signal.fftconvolve(grid, car, 'same')

        for i in xrange(self.height):
            for j in xrange(self.width):
                self.grid[i][j].reachable = int(result[i][j]) == 0

    def neighbours(self, cell, radius=1, unreachables=False, diagonal=True):
        neighbours = set()
        for i in xrange(-radius, radius + 1):
            for j in xrange(-radius, radius + 1):
                x = cell.x + j
                y = cell.y + i
                if 0 <= y < self.height and 0 <= x < self.width and (self.grid[y][x].reachable or unreachables) and (diagonal or (x == cell.x or y == cell.y)):
                    neighbours.add(self.grid[y][x])

        return neighbours

    def search(self, begin, goal):

        if goal.x not in range(self.width) or goal.y not in range(self.height):
            print "Goal is out of bound"
            return []
        elif not self.grid[begin.y][begin.x].reachable:
            print "Beginning is unreachable"
            return []
        elif not self.grid[goal.y][goal.x].reachable:
            print "Goal is unreachable"
            return []
        else:
            # We intialize the closed and open list...
            cl = set()
            ol = set()
            ol.add(begin)

            # ... and the path's beginning
            begin.g = 0
            begin.h = begin.diagonalDistance(goal)
            begin.f = begin.g + begin.h

            while len(ol) > 0:
                curCell = min(ol, key=lambda cell: cell.f)

                if curCell == goal:
                    # We get the path to the current cell, minus the first cell
                    path = curCell.path()[1:]

                    # Before returning the result, we clear the grid (from all weights, parents, ...)
                    self.clear()

                    return path

                # We remove the current cell from the open list and add it to the closed list
                ol.remove(curCell)
                cl.add(curCell)

                for neighbor in self.neighbours(curCell):
                    gScore = curCell.g + curCell.distance(neighbor)

                    if neighbor in cl:
                        if gScore >= neighbor.g:
                            continue

                    if neighbor not in ol or gScore < neighbor.g:
                        neighbor.parent = curCell
                        neighbor.g = gScore
                        neighbor.f = neighbor.g + neighbor.diagonalDistance(goal)
                        if neighbor not in ol:
                            ol.add(neighbor)

            self.clear()
            return []

    def clear(self):
        for line in self.grid:
            for cell in line:
                cell.f = 0
                cell.h = 0
                cell.g = 0
                cell.parent = None

    def display(self):

        dispMatrix = [[' ' for x in range(self.width)] for y in range(self.height)]
        for x in range(self.width):
            for y in range(self.height):
                if self.grid[y][x].reachable:
                    dispMatrix[y][x] = ' '
                else:
                    dispMatrix[y][x] = '#'
        # for cell in self.cl:
        #     dispMatrix[cell.y][cell.x] = 'X'
        for cell in self.path:
            print len(self.path)
            dispMatrix[cell.y][cell.x] = 'o'

        print ' ' + '__'*(1 + self.width)
        for i in range(self.height):
            print '| ',
            for j in range(self.width):
                print dispMatrix[i][j],
            # End of line
            print "|\n",
        print '|' + '__'*(1 + self.width) + '|'
