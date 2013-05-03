# -*- coding: utf8 -*-

"""
    geometry.py - geometry models (shapes, collision, ...)
"""

from math import sqrt, pi, tan, cos, sin, atan2
import numpy as np

def simplifyPath(path, angleEpsilon = 0.3, minDist = 80):
    if len(path) > 2:
        sPath = [path[0]]
        lastPoint = path[1]
        lineCoef = atan2( path[1].y - path[0].y, path[1].x - path[0].x)

        for i in xrange(2, len(path)):
            coef = atan2(path[i].y - path[i - 1].y, path[i].x - path[i - 1].x)
            distFromLast = sqrt( (sPath[-1].x - path[i].x)**2 + (sPath[-1].y - path[i].y)**2 )

            if abs(coef - lineCoef) > angleEpsilon and distFromLast > minDist:
                # New line
                sPath.append(lastPoint)
                lineCoef = coef

            lastPoint = path[i]

        sPath.append(lastPoint)

        return sPath
    else:
        # Can't simplify a path of 2 nodes or less
        return path

def lineMagnitude(p1, p2):
    return sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2)

#Calc minimum distance from a point and a line segment (i.e. consecutive vertices in a polyline).
def DistancePointLine(p, l1, l2):
    #http://local.wasp.uwa.edu.au/~pbourke/geometry/pointline/source.vba
    LineMag = lineMagnitude(l1, l2)
 
    if LineMag < 0.00000001:
        DistancePointLine = 9999
        return DistancePointLine
 
    u1 = (((p.x - l1.x) * (l2.x - l1.x)) + ((p.y - l1.y) * (l2.y - l1.y)))
    u = u1 / (LineMag * LineMag)
 
    if (u < 0.00001) or (u > 1):
        #// closest point does not fall within the line segment, take the shorter distance
        #// to an endpoint
        ix = lineMagnitude(p, l1)
        iy = lineMagnitude(p, l2)
        if ix > iy:
            DistancePointLine = iy
        else:
            DistancePointLine = ix
    else:
        # Intersecting point is on the line, use the formula
        ix = l1.x + u * (l2.x - l1.x)
        iy = l1.y + u * (l2.y - l1.y)
        DistancePointLine = lineMagnitude(p, Point(ix, iy))
 
    return DistancePointLine


def getRamerDouglas(points, epsilon):
    # Find the point with the maximum distance
    dmax = 0
    index = 0
    for i in range(1, len(points) - 2):
        d = DistancePointLine(points[i], points[0], points[len(points) - 1])
        if d > dmax:
            index = i
            dmax = d

    # If max distance is greater than epsilon, recursively simplify
    if dmax >= epsilon:
        # Recursive call
        recResults1 = getRamerDouglas(points[0:index], epsilon)
        recResults2 = getRamerDouglas(points[index:(len(points)-1)], epsilon)
 
        # Build the result list
        ResultList = recResults1[0:(len(recResults1)-2)] + recResults2
    else:
        ResultList = points
    
    # Return the result
    return ResultList


class Point:

    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)

    def distance(self, point):
        return sqrt((point.x - self.x)**2 + (point.y - self.y)**2)

    def translated(self, vector):
        # We're expecting numpy vectors here : [x, y]
        return Point(self.x + vector[0], self.y + vector[1])

    def containedIn(self, shape):
        if isinstance(shape, Rectangle):
            onX = self.x >= shape.boundingRect.origin.x and self.x <= shape.boundingRect.origin.x + shape.boundingRect.width
            onY = self.y >= shape.boundingRect.origin.y and self.y <= shape.boundingRect.origin.y + shape.boundingRect.height
            return onX and onY
        elif isinstance(shape, Ellipse):
            return ((self.x - shape.center.x) / shape.rx)**2 + ((self.y - shape.center.y) / shape.ry)**2 <= 1

    def __str__(self):
        return "Point [{}, {}]".format(self.x, self.y)

    def __sub__(self, point):
        return np.array([self.x - point.x, self.y - point.y])


class Shape(object):
    last_id = 1

    def __init__(self):
        self.id = Shape.last_id
        Shape.last_id += 1
        self.bouningRect = None

    def contains(self, shape):
        self.boundingRect.contains(shape.boundingRect)


# TODO : Finish this
class Polyline(Shape):

    def __init__(self, points, closed=True):
        super(Polyline, self).__init__()

        self.points = points
        self.segments = []

        xmin, ymin = float('inf'), float('inf')
        xmax, ymax = 0, 0

        for i in range(len(points)):
            xmin = min(xmin, points[i].x)
            xmax = max(xmax, points[i].x)
            ymin = min(ymin, points[i].y)
            ymax = max(ymax, points[i].y)

            if (i != len(points)-1) or (closed and len(points) > 2):
                self.segments.append(Segment(points[i].x, points[i].y, points[
                                     (i+1) % len(points)].x, points[(i+1) % len(points)].y))

        self.boundingRect = Rectangle(xmin, xmax, xmax-xmin, ymax-ymin)

    def __str__(self):
        result = "Polyline #{} : ".format(self.id)
        for point in self.points:
            result += point.__str__() + " "
        return result


class Polygone(Shape):

    def __init__(self, points):
        super(Polygone, self).__init__()
        self.border = Polyline(points)
        self.boundingRect = self.border.boundingRect

    def __str__(self):
        result = "Polygone #{} : ".format(self.id)
        for point in self.points:
            result += point.__str__() + " "
        return result


class Rectangle(Shape):

    def __init__(self, x, y, width, height):
        super(Rectangle, self).__init__()
        self.origin = Point(x, y)
        self.width = width
        self.height = height
        self.boundingRect = self

    def contains(self, rect):
        result = self.origin.x <= rect.origin.x and self.origin.y <= rect.origin.y
        result &= self.origin.x+self.width >= rect.origin.x + \
            rect.width and self.origin.y+self.height >= rect.origin.y+rect.height

        return result

    def __str__(self):
        return "Rectangle #{} at {} with {} width and {} height".format(self.id, self.origin, self.width, self.height)


class Ellipse(Shape):

    def __init__(self, cx, cy, rx, ry):
        super(Ellipse, self).__init__()
        self.center = Point(cx, cy)
        self.rx, self.ry = rx, ry
        self.boundingRect = Rectangle(cx-rx, cy-ry, 2*rx, 2*ry)

    def __str__(self):
        return "Ellipse #{} : Center = {} ; rx = {} ; ry = {}".format(self.id, self.center, self.rx, self.ry)


class Ray(object):

    def __init__(self, x, y, angle):
        self.origin = Point(x, y)
        self.angle = angle

        # Infinite distance
        self.length = float('inf')
        # We'd better cache the vector as it's used many many times in collision tests ?
        self.vector = self.vector()

    def vector(self):
        return np.array([cos(self.angle), -sin(self.angle)])

    def intersection(self, shape):
        if isinstance(shape, Segment):
            return self.segmentCollision(shape)
        elif isinstance(shape, Rectangle):
            return self.rectangleCollision(shape)
        elif isinstance(shape, Polyline):
            return self.polylineCollision(shape)
        elif isinstance(shape, Ellipse):
            return self.ellipseCollision(shape)
        else:
            return []

    def polylineCollision(self, polyline):
        result = []

        for segment in polyline.segments:
            intersection = self.intersection(segment)
            if intersection:
                result.append(intersection)
        return result

    def rectangleCollision(self, rectangle):
        x, y = rectangle.origin.x, rectangle.origin.y
        w, h = rectangle.width, rectangle.height

        segments = []
        segments.append(Segment(x, y, x+w, y))
        segments.append(Segment(x+w, y, x+w, y+h))
        segments.append(Segment(x+w, y+h, x, y+h))
        segments.append(Segment(x, y+h, x, y))

        result = []

        for segment in segments:
            intersection = self.intersection(segment)
            if intersection:
                result.append(intersection)
        return result

    def ellipseCollision(self, ellipse):
        # by Ianic

        if self.angle > pi:
            angle = 2*pi - self.angle
        else:
            angle = - self.angle 

        a, b, h, k = ellipse.rx, ellipse.ry, ellipse.center.x, ellipse.center.y
        c = tan(angle)
        d = -c*self.origin.x + self.origin.y

        alpha = c**2 / b**2 + 1. / a**2
        beta = (2*c*(d-k) / b**2) - ( 2*h/(a**2) )
        gamma = h**2/a**2 + (d-k)**2 / b**2 - 1

        delta = beta**2 - 4*alpha*gamma

        if delta < 0:
            return []
        else:
            x1 = (-beta - sqrt(delta)) / (2*alpha)
            y1 = c*x1 + d

            x2 = (-beta + sqrt(delta)) / (2*alpha)
            y2 = c*x2 + d

            collisions = list()
            for point in [Point(x1, y1), Point(x2, y2)]:

                # Determining 
                if -pi/2 < angle < pi/2:
                    if point.x > self.origin.x:
                        collisions.append(point)
                else:
                    if point.x < self.origin.x:
                        collisions.append(point)

            return collisions

    def ellipseCollisionAlt(self, ellipse):
        # Not working !
        """ Alternate implementation by Ahmed.

        We use consider the cartesian formulas of both the ellipse and the line as equal (collision)
        Line : y = a*x + b
        Ellipse : ((x - cx)² / rx²)  + ((y - cy)² / ry²)  = 1

        We end up with this formula :

        (E) <-> (ry² + (a*rx)²) x² + (rx²*(2*a*b -2*a*cy) - 2*ry²*cx) x + ( (ry*cx)² + rx²*(b² - 2*b*cy + cy²) - (rx*ry)² ) = 0

        Let's consider alpha = (ry² + (a*rx)²) ; beta = (rx²*(2*a*b -2*a*cy) - 2*ry²*cx)
        and omega = (ry*cx)² + rx²*(b² - 2*b*cy + cy²) - (rx*ry)**2

        We have : (E) <-> alpha * x² + beta * x + omega = 0

        So the solutions are (with delta = beta**2 - 4*alpha*omega) if delta >= 0:
        1) x = (- beta - sqrt(delta)) / (2*alpha)
        2) x = (-beta + sqrt(delta)) / (2*alpha)
        """

        cx, cy, rx, ry = ellipse.center.x, ellipse.center.y, ellipse.rx, ellipse.ry

        if self.angle > pi:
            angle = - 2*pi + self.angle
        else:
            angle = - self.angle 

        a = tan(angle)
        b = self.origin.y - self.origin.x * tan(angle)

        alpha = ry**2 + (a*rx)**2
        beta = rx**2 * (2*a*b - 2*a*cy) - 2 * ry**2 * cx
        omega = rx**2 * (b**2 - 2*b*cy + cy**2) - (rx*ry)**2

        delta = beta**2 - 4 * alpha * omega

        if delta < 0:
            return []
        else:
            x1 = float(-beta - sqrt(delta)) / (2*alpha)
            x2 = float(-beta + sqrt(delta)) / (2*alpha)

            y1 = a*x1 + b
            y2 = a*x2 + b

            return [Point(x1, y1), Point(x2, y2)]

    def segmentCollision(self, segment):
        """
        Implementation of this :
        Intersection <=> p + t r = q + u s
        t = (q - p) x s / (r x s)
        u = (q - p) x r / (r x s)
        With : q : self's origin ;  s : self.vector ; p : segment's origin ; r : segment.vector
        Conditions : r x s =/= 0 ; 0 <= t <= |segment| and 0 <= u <= |self| (knowing that the norm can be infinite, for a ray)
        """

        q = self.origin
        p = segment.origin
        s = self.vector
        r = segment.vector

        if np.cross(r, s) == 0:
            return None
        else:
            q_minus_p = np.array([q.x - p.x, q.y - p.y])
            u = float(np.cross(q_minus_p, s)) / np.cross(r, s)
            t = float(np.cross(q_minus_p, r)) / np.cross(r, s)

            if u < 0 or u > segment.length or t < 0 or t > self.length:
                return None
            else:
                # print "Intersection with ", segment
                x, y = q.x + t*r[0], q.y + t*r[1]
                return Point(x, y)

    def __str__(self):
        return "Ray from {} with {}radians angle".format(self.origin, self.angle)


class Segment(Ray):

    def __init__(self, x1, y1, x2, y2):
        # Calculating heading angle
        angle = pi - atan2(y1 - y2, x1 - x2)

        super(Segment, self).__init__(x1, y1, angle)
        # Calculating distance
        self.length = sqrt((x1-x2)**2 + (y1-y2)**2)

    def __str__(self):
        return "Segment [ {}, {} ]".format(self.origin, self.origin.translated(self.vector*self.length))

if __name__ == "__main__":

    # seg1 = Segment(0, 0, 1, 1)
    # seg2 = Segment(0, 2, 2, 0)
    # print seg1
    # print seg1.vector
    # print seg1.angle
    # print "Testing intersection between {} and {}".format(seg1, seg2)
    # intersection = seg1.intersection(seg2)
    # if intersection:
    #   print "Intersection at {} | Distance : {}".format(intersection, seg1.origin.distance(intersection))
    # else:
    #   print "No intersection between {} and {} !".format(seg1, seg2)

    point = Point(3, 5)
    rect = Rectangle(0, 0, 4, 4)
    if point.containedIn(rect):
        print point, "contained in", rect
    else:
        print point, "not contained in", rect
