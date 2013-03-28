import math
import numpy as np

class Point:
	def __init__(self, x, y):
		self.x = int(x)
		self.y = int(y)

	def distance(self, point):
		return math.sqrt((point.x - self.x)**2 + (point.y - self.y)**2)

	def translated(self, vector):
		# We're expecting numpy vectors here : [x, y]
		return Point(self.x + vector[0], self.y + vector[1])

	def containedIn(self, shape):
		if isinstance(shape, Rectangle):
			onX = self.x >= shape.boundingRect.origin.x and self.x <= shape.boundingRect.origin.x + shape.boundingRect.width
			onY = self.y >= shape.boundingRect.origin.y and self.y <= shape.boundingRect.origin.y + shape.boundingRect.height
			return onX and onY
		elif isinstance(shape, Ellipse):
			return ( (self.x - shape.center.x) / shape.rx )**2 + ( (self.y - shape.center.y) / shape.ry )**2 <= 1

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


#TODO : Finish this
class Polyline(Shape):
	def __init__(self, points, closed = True):
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

			if (i != len(points)-1) or (closed and len(points)>2):
				self.segments.append(Segment(points[i].x, points[i].y, points[(i+1)%len(points)].x, points[(i+1)%len(points)].y))

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
		result &= self.origin.x+self.width >= rect.origin.x+rect.width and self.origin.y+self.height >= rect.origin.y+rect.height

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

		#Infinite distance
		self.length = float('inf')
		#We'd better cache the vector as it's used many many times in collision tests ?
		self.vector = self.vector()

	def vector(self):
		return np.array([math.cos(self.angle), -math.sin(self.angle)])

	def intersection(self, shape):
		if isinstance(shape, Segment):
			return self.segmentCollision(shape)
		elif isinstance(shape, Rectangle):
			return self.rectangleCollision(shape)
		elif isinstance(shape, Polyline):
			return self.polylineCollision(shape)
		elif isinstance(shape, Ellipse):
			return []
			#return self.ellipseCollision(shape)
		else:
			print "COLLISION NOT IMPLEMENTED"
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
			q_minus_p = np.array( [q.x - p.x, q.y - p.y ] )
			u = float(np.cross(q_minus_p, s)) / np.cross(r, s)
			t = float(np.cross(q_minus_p, r)) / np.cross(r, s)

			if u<0 or u>segment.length or t<0 or t>self.length:
				return None
			else:
				# print "Intersection with ", segment
				x, y = q.x + t*r[0] , q.y + t*r[1]
				return Point(x, y)

	def __str__(self):
		return "Ray from {} with {}radians angle".format(self.origin, self.angle)

class Segment(Ray):
	def __init__(self, x1, y1, x2, y2):
		# Calculating heading angle
		angle = math.pi - math.atan2(y1- y2, x1- x2)
		if angle > math.pi:
			angle = angle - 2*math.pi

		super(Segment, self).__init__(x1, y1, angle)
		#Calculating distance
		self.length = math.sqrt((x1-x2)**2 + (y1-y2)**2)

	def __str__(self):
		return "Segment [ {}, {} ]".format(self.origin, self.origin.translated(self.vector*self.length))

if __name__=="__main__":

	# seg1 = Segment(0, 0, 1, 1)
	# seg2 = Segment(0, 2, 2, 0)
	# # print seg1
	# # print seg1.vector
	# # print seg1.angle
	# print "Testing intersection between {} and {}".format(seg1, seg2)
	# intersection = seg1.intersection(seg2)
	# if intersection:
	# 	print "Intersection at {} | Distance : {}".format(intersection, seg1.origin.distance(intersection))
	# else:
	# 	print "No intersection between {} and {} !".format(seg1, seg2)

	point = Point(3, 5)
	rect = Rectangle(0, 0, 4, 4)
	if point.containedIn(rect):
		print point, "contained in", rect
	else:
		print point, "not contained in", rect
