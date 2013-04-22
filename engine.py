"""
    engine.py - all what's related to the car: model (coordinates, heading angle, ...) and graphic representation (with Qt)
"""

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

	def __init__(self, map = None, x = 0, y = 0, width = default_width, length = default_length, sprite_name = "sedan", shadow = True):
		super(Car, self).__init__()

		pen = QtGui.QPen()

		#The map where the car is located
		self.map = map
		#This should be in the map, but keep it here for test purpose :s

		#Model related attributes
		self.width = width
		self.length = length

		# Setting up text
		self.text = QtGui.QGraphicsTextItem("", self)
		self.text.setFont(QtGui.QFont("Ubuntu-L.ttf"))
		self.text.setPos(-140, -140)

		self.textShadow = QtGui.QGraphicsDropShadowEffect()
		self.textShadow.setBlurRadius(3)
		self.textShadow.setColor( QtGui.QColor(0, 0, 0) )
		self.textShadow.setOffset(1, 1)
		self.text.setGraphicsEffect( self.textShadow )

		self.text.setDefaultTextColor(QtGui.QColor(210, 220, 250))
		self.text.font().setBold(True)

		# Initializing image
		self.sprite_name = sprite_name
		self.img = Car.sprites[sprite_name]

		self.image = QtGui.QGraphicsPixmapItem( QtGui.QPixmap( Car.sprites[sprite_name] ), self)
		self.image.setOffset(-self.img.width()/2, -self.img.height()/2)

		# Shadow effect on the car image
		if shadow:
			self.shadow = QtGui.QGraphicsDropShadowEffect()
			self.shadow.setBlurRadius(80)
			self.shadow.setColor( QtGui.QColor(80, 90, 220) )
			self.shadow.setOffset(0, 0)
			self.image.setGraphicsEffect( self.shadow )

		# Initializing the "view ray"
		self.line = QtCore.QLine(x, y, 0, 0)
		self.ray = QtGui.QGraphicsLineItem(self.line, self )
		self.ray.setZValue(-1)

		pen.setColor(QtGui.QColor(180, 200, 200))
		pen.setWidth(2)
		self.ray.setPen(pen)

		self.speed = 0

		# Distance to the closest object ahead
		self.distance = None

		# True when the car is moving :
		self.moving = False

		#Angle is in radian, and follows the traditional trigonometric orientation
		#	   pi/2
		#  -pi __|__ 0
		#		 |
		# 	  -pi/2
		self.angle = 0

		self.setPos(x, y)


		# Some config infos.
		self.setCacheMode( QtGui.QGraphicsItem.ItemCoordinateCache )


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

	def setCaption(self, text):
		self.text.setPlainText(text)

	def paint(self, painter=None, style=None, widget=None):
		pass


	def update(self):
		super(Car, self).update()

		#Calculating the distance to the closest object
		if self.map and not self.moving:
			self.distance = self.map.rayDistance(self.x(), self.y(), self.angle)

		#Updating the caption
		if self.moving:
			self.setCaption( "Car moving... " )
			distance = 0
		elif self.distance:
			self.setCaption( "Closest object at : {}".format(int(self.distance)) )
			distance = self.distance
		else:
			self.setCaption( "No object ahead" )
			distance = 0

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