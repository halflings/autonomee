"""
astar.py - A* algorithm implementation
"""

from geometry import Point
from math import sqrt
from time import sleep

class Cell(object):
    def __init__(self, x, y, reachable = True):
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

    def manhattanDistance(self, cell):
        return abs(self.x - cell.x) + abs(self.y - cell.y)

    # Calculates the cell's score
    def process(self, parent, goal):
        self.parent = parent
        self.g = parent.distance(self)
        self.h = self.manhattanDistance(goal)
        self.f = self.g + self.h

    def path(self):
        resPath = [self]
        cell = self
        while cell.parent != None :
            resPath.append(cell.parent)
            cell = cell.parent
        return reversed(resPath)

    def __str__(self):
        """ String representation,  for debugging only """
        strRep = "Cell [{}, {}]".format(self.x, self.y)
        if not self.reachable:
            strRep += " | Is a wall."

        return strRep

class DiscreteMap:

    def __init__(self, SvgMap, division = 5, radius = 20):
        self.division = division

        self.width = int(SvgMap.width/division)
        self.height = int(SvgMap.height/division)

        self.grid = [ [ False for x in range(self.width) ] for y in range(self.height) ]

        # Open and closed list, used for A* algorithm
        self.ol = set()
        self.cl = set()

        self.path = []

        for y in range(self.height):
            for x in range(self.width):
                # The cell (x, y) will represent this point :
                point = Point((x + 0.5)*division, (y + 0.5)*division)

                # We check if any of the map's shapes contain our point
                obstacle = False
                id = 0

                # TODO : Change this to take into account the car's width
                while not obstacle and id<len(SvgMap.shapes):
                    obstacle = point.containedIn(SvgMap.shapes[id])
                    id += 1

                if obstacle:
                    self.grid[y][x] = Cell(x, y, reachable = False)
                else:
                    self.grid[y][x] = Cell(x, y, reachable = True)

        # Then we eliminate all the cells that are too close to obstacles
        unreachable = set()
        for line in self.grid:
            for cell in line:
                # print len(unreachable)
                if not cell.reachable:
                    unreachable.add(cell)

        print "test"
        for cell in unreachable:
            for nCell in self.neighbours( cell, int(radius/division) ):
                nCell.reachable = False

        for cell in unreachable:
            cell.reachable = False


    def neighbours(self, cell, radius = 1):
        neighbours = set()
        for i in xrange(-radius, radius + 1):
            for j in xrange(-radius, radius + 1):
                x = cell.x + j
                y = cell.y + i
                if y in range(0, self.height) and x in range(0, self.width):
                    if self.grid[y][x].reachable:
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

            self.cl = set()
            self.ol = set()

            curCell = begin
            self.ol.add(curCell)

            while len(self.ol) > 0:

                # We choose the cell in the open list having the minimum score as our current cell
                curCell = min(self.ol, key = lambda cell : cell.f)

                # We add the current cell to the closed list
                self.ol.remove(curCell)
                self.cl.add(curCell)

                # We check the cell's (reachable) neighbours :
                neighbours = self.neighbours(curCell)

                for cell in neighbours:
                    # If the goal is a neighbour cell :
                    if cell == goal:
                        cell.parent = curCell
                        self.path = cell.path()
                        # self.display()
                        self.clear()
                        return self.path
                    elif cell not in self.cl:
                        # We process the cells that are not in the closed list
                        # (processing <-> calculating the "F" score)
                        cell.process(curCell, goal)

                        self.ol.add(cell)

                # To vizualize the algorithm in ASCII
                # self.display()
                # sleep(0.02)

            # If the open list gets empty : no path can be found
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

        dispMatrix = [ [ ' ' for x in range(self.width) ] for y in range(self.height) ]
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
        print '|'+ '__'*(1 + self.width) + '|'
