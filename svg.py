from lxml import etree
from geometry import *
import math
import re
NS = {'svg': 'http://www.w3.org/2000/svg',
'sodipodi': 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd'}

def remove_ns(text, namespace = NS['svg']):
	pattern = "{" + namespace + "}([\S]+)"
	match = re.match(pattern, text)
	if match:
		return match.group(1)
	else:
		return text

def add_ns(text, namespace = NS['sodipodi']):
	return '{' + namespace + '}' + text


class SvgTree:
	default_title = "Undefined title"
	points_pattern = "(?:([-]?\d+\.?\d*),([-]?\d+\.?\d*))"

	def __init__(self, path="map/mapexample.svg"):
		#Shapes' list
		self.shapes = []

		#SVG file parsing : opening the file, setting up a custom parser
		self.svg_file = open(path)
		parser=etree.XMLParser(ns_clean=True, remove_comments=True, remove_blank_text=True)
		#Generating a parsing tree
		tree=etree.parse(self.svg_file, parser)

		#Parsing the title
		titleParse =tree.xpath("//n:text[@id='Titre']/n:tspan/text()",
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

		### Parsing SHAPES
		### We search all the groups and subgroups and parse their elements
		###################################################################

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

					ellipse = EllipseFactory(cx, cy, rx, ry)
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

				rectangle = RectangleFactory(x, y, w, h)
				print "PARSED : ", rectangle
				self.shapes.append(rectangle)

		#PARSING POLYGONES
		polygones = tree.xpath("//n:polygone",
                 namespaces={'n': NS['svg']})
		if polygones:
			for polygone in polygones:
				points = self.parse_points(polygone.attrib['points'])

				polygone = Polygone(points)
				print "PARSED : ", polygone
				self.shapes.append(polygone)

		#PARSING POLYLINES
		polylines = tree.xpath("//n:polyline",
         namespaces={'n': NS['svg']})

		if polylines:
			for poly in polylines:
				points = self.parse_points(poly.attrib['points'])
				polyline = Polyline(points)
				print "PARSED : ", polyline
				self.shapes.append(polyline)

		#self.discretize()

	@staticmethod
	def parse_points(svg_rep):
		points = []
		search = re.findall(SvgTree.points_pattern, svg_rep)
		for point in search:
			x = float(point[0])
			y = float(point[1])
			points.append(Point(x, y))
		return points

	def RayDistance(self, x, y, headingAngle):
		ray = Ray(x, y, headingAngle)
		minDist = None
		for shape in self.shapes:
			intersections = ray.intersection(shape)
			# if intersections:
			# 	print "Intersection at :"
			for intersection in intersections:
				# print intersection
				distance = intersection.distance(ray.origin)
				# print "Shape {} ; Intersection {} ; Distance {}".format(shape, intersection, distance)
				if minDist == None:
					minDist = distance
				elif distance < minDist:
					minDist = distance

		return minDist

	#FOR PATHFINDING, should optimize this
	def discretize(self):
		for i in range(int(self.width/20)):
			for j in range(int(self.height/20)):
				point = Point(i*20, j*20)
				obstacle = False
				i = 0
				while not obstacle and i<len(self.shapes):
					obstacle = point.containedIn(self.shapes[i])
					i+=1
				if obstacle:
					print '#',
				else:
					print ' ',

			print '\n',




	def __str__(self):
		result = 'SVG Tree - "{}"\n'.format(self.title)
		result += "Width : {}{} | Height : {}{} \n".format(self.width, self.width_unit,
			self.height, self.height_unit)
		result += '#'*40 + '\n'*2
		for shape in self.shapes:
			result += shape.__str__() + '\n'

		return result


if __name__=="__main__":

	mySvg = SvgTree("mapexample.svg")
	print mySvg