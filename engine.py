from PySide import QtCore, QtGui
import math
from math import cos, sin

class Car(QtGui.QGraphicsObject):
	#"ALL measurements must be in mm"
	# NOTE : The mm/px conversion should be done in the model ... maybe this class should do everything in px ...
	default_width = 100
	default_length = 200

	default_image =  QtGui.QImage("img/car.png")
	scale_factor = 0.5
	sprites = {"sedan" : default_image.scaledToWidth(default_image.width()*scale_factor)}

	def __init__(self, map = None, x = 0, y = 0, width = default_width, length = default_length, sprite_name = "sedan"):
		super(Car, self).__init__()

		#The map where the car is located
		self.map = map
		#This should be in the map, but keep it here for test purpose :s

		#Model related attributes
		self.width = width
		self.length = length

		# Setting up text
		self.caption = ""
		self.text = QtGui.QGraphicsTextItem("", self)
		self.text.setFont(QtGui.QFont("Ubuntu-L.ttf"))
		self.text.setPos(-140, -140)


		# Initializing image
		self.sprite_name = sprite_name
		self.img = Car.sprites[sprite_name]

		self.image = QtGui.QGraphicsPixmapItem( QtGui.QPixmap( Car.sprites[sprite_name] ), self)
		self.image.setOffset(-self.img.width()/2, -self.img.height()/2)
		self.image.setZValue(-1)

		# Initializing the "view ray"
		self.line = QtCore.QLine(x, y, 0, 0)
		self.ray = QtGui.QGraphicsLineItem(self.line, self )

		self.speed = 0
		self.distance = None

		#Angle is in radian, and follows the traditional trigonometric orientation
		#			   pi/2
		#	pi or -pi __|__ 0
		#				|
		#			  -pi/2
		self.angle = 0

		self.setPos(x, y)

		# True when the car is moving :
		self.moving = False

		#print "Car width {} | Car length {} | Car sprite {}".format(self.width, self.length, self.sprite)

		#Some random flags ... (should be useful later)
		self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)
		self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)

		self.rect = QtCore.QRectF()
		self.update()

	def move(self, speed):

		dx = speed * cos(self.angle)
		dy = -speed * sin(self.angle)

		self.setPos( int(self.x() + dx) , int(self.y() + dy) )

		self.update()

	def setAngle(self, val):
		#Updating angle
		self.angle = val

		# Rotating the car around its center
		self.image.setRotation(-math.degrees(self.angle))

		self.update()

	def readAngle(self):
		return self.angle

	angleProperty = QtCore.Property(float, readAngle, setAngle)


	def setPos(self, x, y):
		super(Car, self).setPos(x, y)
		self.update()

	def paint(self, painter=None, style=None, widget=None):
		pass
		pen = QtGui.QPen()
		pen.setColor(QtGui.QColor(20, 80, 228))
		pen.setWidth(2)
		painter.setPen(pen)


	def update(self):
		super(Car, self).update()

		#Calculating the distance to the closest object
		if self.map:
			self.distance = self.map.RayDistance(self.x(), self.y(), self.angle)

		#Updating the caption

		if self.distance:
			self.caption = "Closest object at : {}".format(int(self.distance))
			distance = self.distance
		else:
			self.caption = "No object ahead"
			distance = 0

		self.text.setPlainText(self.caption)

		# Updating the "ray"
		self.ray.setLine(QtCore.QLine(0, 0, distance*math.cos(self.angle), - distance*math.sin(self.angle)))

	def boundingRect(self):
		return QtCore.QRectF(self.x(), self.y(), self.image.boundingRect().width() , self.image.boundingRect().height())

	def x(self):
		return self.pos().x()
	def y(self):
		return self.pos().y()

	def frontX(self):
		return self.x() + cos(self.angle) * self.img.width()
	def frontY(self):
		return self.y() - sin(self.angle) * self.img.width()

	def topLeftX(self):
		return self.x() - ( self.image.boundingRect().width() / 2 )

	def topLeftY(self):
		return self.y() - ( self.image.boundingRect().height() / 2 )

	def formatAngle(self, angle):
		return (angle + math.pi)%(2*math.pi) - math.pi

	# def mousePressEvent(self, event):
	# 	super(Car, self).mousePressEvent(event)
	# 	print "Car mouse event at ({} , {})".format(event.pos().x(), event.pos().y())

	# 	event.accept()