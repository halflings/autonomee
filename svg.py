"""
svg.py - module to parse geometric elements from an svg file.
"""

from lxml import etree
from geometry import Point, Rectangle, Ellipse, Polygone, Polyline, Ray
from astar import DiscreteMap, Cell
import re
NS = {'svg': 'http://www.w3.org/2000/svg',
      'sodipodi': 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd'}

float_pattern = "-?\d+(?:[.]\d+)?"
translatePattern = "translate[(]({}),({})[)]".format(float_pattern, float_pattern)

def remove_ns(text, namespace=NS['svg']):

    pattern = "{" + namespace + "}([\S]+)"
    match = re.match(pattern, text)
    if match:
        return match.group(1)
    else:
        return text

def add_ns(text, namespace=NS['sodipodi']):
    return '{' + namespace + '}' + text

def parseTransform(element):
    if 'transform' in element.attrib:
        transform = element.attrib['transform']
        regex = re.search(translatePattern, transform)
        if regex:
            return float(regex.group(1)), float(regex.group(2))

    return 0, 0

class SvgTree:

    default_title = "Undefined title"
    points_pattern = "(?:([-]?\d+\.?\d*),([-]?\d+\.?\d*))"

    @staticmethod
    def parse_points(svg_rep):
        points = []
        search = re.findall(SvgTree.points_pattern, svg_rep)
        for point in search:
            x = float(point[0])
            y = float(point[1])
            points.append(Point(x, y))
        return points

    def __init__(self, path, radius=5):
        #Shapes' list
        self.shapes = []

        self.path = path

        #SVG file parsing : opening the file, setting up a custom parser
        self.svg_file = open(path)
        parser = etree.XMLParser(ns_clean=True, remove_comments=True,
                                 remove_blank_text=True)
        #Generating a parsing tree
        tree = etree.parse(self.svg_file, parser)

        #Parsing the title
        titleParse = tree.xpath("//n:text[@id='Titre']/n:tspan/text()",
                                namespaces={'n': NS['svg']})
        if titleParse:
            self.title = titleParse[0]
        else:
            self.title = SvgTree.default_title

        #Parsing the SVG's parameters (width, height, ...)
        for attribute in ['width', 'height']:
            param = tree.xpath("//n:svg",
                               namespaces={'n': NS['svg']})[0]
            regexp = re.match("([\d]+)(.+)", param.attrib[attribute])
            if regexp:
                setattr(self, attribute, int(regexp.group(1)))
                setattr(self, attribute+'_unit', regexp.group(2))
            else:
                raise "No {} ! Can't parse SVG.".format(attribute)

        #Bounding rectangle ( TODO : mm -> xp, etc.)
        self.rect = Rectangle(-1, -1, self.width+1, self.height+1)


        ######################################################################
        ### Parsing SHAPES                                                  ##
        ### We search all the groups and subgroups and parse their elements ##
        ######################################################################

        #PARSING PATHS (polylines and ellipses)
        paths = tree.xpath("//n:path",
                 namespaces={'n': NS['svg']})
        #We'll add the "sodipodi" namespace here because arc shapes (like ellipsis) use it
        sodipodi_type = add_ns('type', NS['sodipodi'])
        if paths:
            for path in paths:
                if sodipodi_type in path.attrib and path.attrib[sodipodi_type]=='arc':
                    cx = float(path.attrib[add_ns('cx', NS['sodipodi'])])
                    cy = float(path.attrib[add_ns('cy', NS['sodipodi'])])
                    rx = float(path.attrib[add_ns('rx', NS['sodipodi'])])
                    ry = float(path.attrib[add_ns('ry', NS['sodipodi'])])

                    dx, dy = parseTransform(path)
                    cx, cy = cx + dx, cy + dy

                    ellipse = Ellipse(cx, cy, rx, ry)
                    self.shapes.append(ellipse)
                else:
                    print "[ ! ] Paths - except ellipses - are not implemented yet"
                    # points = self.parse_points(path.attrib['d'])
                    # print points

        #PARSING RECTANGLES
        rectangles = tree.xpath("//n:rect",
                 namespaces={'n': NS['svg']})
        if rectangles:
            for rect in rectangles:
                x = float(rect.attrib['x'])
                y = float(rect.attrib['y'])
                w = float(rect.attrib['width'])
                h = float(rect.attrib['height'])

                dx, dy = parseTransform(rect)
                x, y = x + dx, y + dy

                rectangle = Rectangle(x, y, w, h)
                self.shapes.append(rectangle)

        #PARSING POLYGONES
        polygones = tree.xpath("//n:polygone",
                 namespaces={'n': NS['svg']})
        if polygones:
            for polygone in polygones:
                points = self.parse_points(polygone.attrib['points'])

                dx, dy = parseTransform(polygone)
                for point in points:
                    point.x += dx
                    point.y += dy

                polygone = Polygone(points)
                self.shapes.append(polygone)

        #PARSING POLYLINES
        polylines = tree.xpath("//n:polyline",
         namespaces={'n': NS['svg']})

        if polylines:
            for poly in polylines:
                points = self.parse_points(poly.attrib['points'])

                dx, dy = parseTransform(poly)
                for point in points:
                    point.x += dx
                    point.y += dy

                polyline = Polyline(points)
                self.shapes.append(polyline)

        self.discreteMap = DiscreteMap(self, radius=radius)


    def setRadius(self, radius):
        self.discreteMap.setRadius(radius)

    def isObstacle(self, x, y):
        """
        True if there's an obstacle in (x, y), false otherwise
        """
        point = Point(x, y)
        obstacle = False
        id = 0

        while not obstacle and id<len(self.shapes):
            obstacle = point.containedIn(self.shapes[id])
            id += 1

        return obstacle


    def rayDistance(self, x, y, headingAngle):
        ray = Ray(x, y, headingAngle)
        dist = None

        for shape in self.shapes:
            intersections = ray.intersection(shape)

            if len(intersections) > 0:
                closestIntersect = min(intersect.distance(ray.origin) for intersect in intersections)
                if dist is None:
                    dist = closestIntersect
                else:
                    dist = min(dist, closestIntersect)

        if dist is None:
            # If there's no intersection with any shape, we test for intersections with the map's borders
            dist = min(intersect.distance(ray.origin) for intersect in ray.intersection(self.rect))

        return dist

    def search(self, begin, goal):
        div = self.discreteMap.division
        beginCell = Cell(begin[0] / div, begin[1] / div)
        goalCell = Cell(goal[0] / div, goal[1] / div)

        path = self.discreteMap.search(beginCell, goalCell)
        points = []
        if path:
            for cell in path:
                points.append(Point(cell.x * div, cell.y * div))

        return points

    def __str__(self):
        result = 'SVG Tree - "{}"\n'.format(self.title)
        result += "Width : {}{} | Height : {}{} \n".format(self.width, self.width_unit,
                  self.height, self.height_unit)
        result += '#'*40 + '\n'*2
        for shape in self.shapes:
            result += shape.__str__() + '\n'

        return result


if __name__=="__main__":

    mySvg = SvgTree("maps/laby.svg")
    print mySvg
    print ""
    path = mySvg.discreteMap.search(Cell(0, 0), Cell(40, 40))
