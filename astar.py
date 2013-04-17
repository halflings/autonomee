"""
astar.py - A* algorithm implementation
"""

from geometry import Point
from math import sqrt
from time import sleep
import scipy
import scipy.signal
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


    diagonalCost = sqrt(2)
    straightCost = 1

    def heuristicDistance(self, cell):
        return self.manhattanDistance(cell)

    def manhattanDistance(self, cell):
        return abs(self.x - cell.x) + abs(self.y - cell.y)

    def diagonalDistance(self, cell):
        # hDiagonal = min(abs(self.x-cell.x), abs(self.y-cell.y))
        # hStraight = (abs(self.x-cell.x) + abs(self.y-cell.y))

        # return Cell.diagonalCost * hDiagonal + Cell.straightCost * (hStraight - 2*hDiagonal)

        xDist = abs(self.x - cell.x)
        yDist = abs(self.y - cell.y)

        if xDist > yDist:
            return 1.4 * yDist + (xDist - yDist)
        else:
            return 1.4 * xDist + (yDist - xDist)

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
            strRep += " (wall)"

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


        # ALGORITHM EXPLOITING CONVOLUTION

        # 1 : Unreachable ; 0 : Reachable
        car = scipy.array( [[1 for i in xrange(radius)] for j in xrange(radius)] )
        grid = scipy.array( [[0 if self.grid[i][j].reachable else 1 for j in xrange(self.width)] for i in xrange(self.height)] )

        result = scipy.signal.fftconvolve( grid, car, 'same' )

        for i in xrange(self.height):
            for j in xrange(self.width):
                self.grid[i][j].reachable = True if int(result[i][j]) == 0 else False


        # Then we eliminate all the cells that are too close to obstacles


        # ALGO 1 : Go on each reachable cell, check if a neighbour is unreachable
        # toEliminate = set()

        # for line in self.grid:
        #     for cell in line:
        #         if cell.reachable:
        #             neighbours = self.neighbours( cell, radius = int(radius/division), unreachables = True )
        #             obstacle = False
        #             for c in neighbours:
        #                 if not c.reachable:
        #                     obstacle = True
        #                     break

        #             if obstacle:
        #                 toEliminate.add(cell)

        # for cell in toEliminate:
        #     cell.reachable = False

        # ALGO 1 END --


        # ALGO 2 : Go on each unreachable cell,

        # unreachable = set()
        # for line in self.grid:
        #     for cell in line:
        #         # print len(unreachable)
        #         if not cell.reachable:
        #             unreachable.add(cell)

        # for cell in unreachable:
        #     neighbours = self.neighbours( cell, int(radius/division) )
        #     for nCell in neighbours:
        #         nCell.reachable = False


    def neighbours(self, cell, radius = 1, unreachables = False, diagonal = True):
        neighbours = set()
        for i in xrange(-radius, radius + 1):
            for j in xrange(-radius, radius + 1):
                x = cell.x + j
                y = cell.y + i
                if 0 <= y < self.height and 0 <= x < self.width and ( self.grid[y][x].reachable or unreachables ) and (diagonal or (x == cell.x or y == cell.y)) :
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

            #We intialize the closed and open list
            cl  = set()
            ol = set()
            ol.add(begin)

            #We initialize the
            begin.g = 0
            begin.h = begin.diagonalDistance(goal)
            begin.f = begin.g + begin.h

            while len(ol) > 0:
                curCell = min(ol, key = lambda cell : cell.f)

                if curCell == goal:
                    path = curCell.path()
                    self.clear()
                    return path


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





    def altsearch(self, begin, goal):
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
                neighbours = self.neighbours(curCell, diagonal = True)

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
