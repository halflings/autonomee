"""
    engine.py - all what's related to the car: model (coordinates, heading angle, ...) and graphic representation (with Qt)
"""

from PySide.QtCore import *
from PySide.QtGui import *

import math
from math import cos, sin

DEFAULT_IMAGE = QImage("img/car.png")
SPRITES = {"sedan" : DEFAULT_IMAGE.scaledToWidth(DEFAULT_IMAGE.width()*0.4)}



def formatAngle(angle):
	""" Formats angle in the trigonometric convention """
	return (angle + math.pi)%(2*math.pi) - math.pi

class Car(QObject):

	# TODO : Should be in mm ?
	default_width = 100
	default_length = 200

	def __init__(self, map=None, x=0, y=0, width=default_width, length=default_length):
		super(Car, self).__init__()

		#The map where the car is located
		self.map = map

		self.x = x
		self.y = y

		self.width = width
		self.length = length

		self.speed = 0

		# Distance to the closest object ahead
		self.distance = None

		# True when the car is moving :
		self.moving = False

		#Angle is in radian, and follows the traditional trigonometric convention
		#	   pi/2
		#  -pi __|__ 0
		#		 |
		# 	  -pi/2
		self.angle = 0

		self.views = set()

	def addView(self, view):
		self.views.add(view)
	def removeView(self, view):
		if view in self.views:
			self.views.remove(view)

	def move(self, speed):
		self.x += speed * cos(self.angle)
		self.y += speed * -sin(self.angle)

		self.update()

	def readAngle(self):
		return self.angle

	def setAngle(self, angle):
		self.angle = formatAngle(angle)

		self.update()

	angleProperty = Property(float, readAngle, setAngle)


	def readPosition(self):
		return (self.x, self.y)
	def setPosition(self, position):
		self.x, self.y = position.x(), position.y()

	positionProperty = Property(QPointF, readPosition, setPosition)

	def update(self):
		# Calculating the distance to the closest object
		if self.map is not None and not self.moving:
			self.distance = self.map.rayDistance(self.x, self.y, self.angle)

		# print self

		for view in self.views:
			view.update()

	def __repr__(self):
		return "Angle : {} | Position ({}, {}) | Distance : {}".format(self.angle, self.x, self.y, self.distance)


class GraphicsCarItem(QGraphicsObject):
	#"ALL measurements must be in mm"
	# NOTE : The mm/px conversion should be done in the model ... maybe this class should do everything in px ...
	default_width = 100
	default_length = 200
	scale_factor = 0.5


	def __del__(self):
		print "DESTORY"

	def __init__(self, car, sprite_name = "sedan", shadow = True):
		super(GraphicsCarItem, self).__init__()


		pen = QPen()

		self.car = car
		self.car.addView(self)

		# Setting up text
		self.text = QGraphicsTextItem("", self)
		self.text.setFont(QFont("Ubuntu-L.ttf"))
		self.text.setPos(-140, -140)

		self.textShadow = QGraphicsDropShadowEffect()
		self.textShadow.setBlurRadius(3)
		self.textShadow.setColor( QColor(0, 0, 0) )
		self.textShadow.setOffset(1, 1)
		self.text.setGraphicsEffect( self.textShadow )

		self.text.setDefaultTextColor(QColor(210, 220, 250))
		self.text.font().setBold(True)

		# Initializing image
		self.sprite_name = sprite_name
		self.img = SPRITES[sprite_name]

		self.image = QGraphicsPixmapItem( QPixmap( SPRITES[sprite_name] ), self)
		self.image.setOffset(-self.img.width()/2, -self.img.height()/2)

		# Shadow effect on the car's image
		if shadow:
			self.shadow = QGraphicsDropShadowEffect()
			self.shadow.setBlurRadius(80)
			self.shadow.setColor( QColor(80, 90, 220) )
			self.shadow.setOffset(0, 0)
			self.image.setGraphicsEffect( self.shadow )

		# Initializing the "view ray"
		self.line = QLine(self.car.x, self.car.y, 0, 0)
		self.ray = QGraphicsLineItem(self.line, self )
		self.ray.setZValue(-1)

		pen.setColor(QColor(180, 200, 200))
		pen.setWidth(2)
		self.ray.setPen(pen)

		# Caching for the graphics
		self.setCacheMode( QGraphicsItem.ItemCoordinateCache )

		self.rect = QRectF()
		self.update()

	def setCaption(self, text):
		self.text.setPlainText(text)

	def paint(self, painter=None, style=None, widget=None):
		pass

	def update(self):
		super(GraphicsCarItem, self).update()

		# Rotating the car around its center
		if self.image.rotation() != self.car.angle:
			self.image.setRotation(-math.degrees(self.car.angle))

		self.setPos(self.car.x, self.car.y)

		#Updating the caption
		distance = 0
		if self.car.moving:
			self.setCaption( "Car moving... " )
		elif self.car.distance:
			self.setCaption( "Closest object at : {}".format(int(self.car.distance)) )
			distance = self.car.distance
		else:
			self.setCaption( "No object ahead" )

		# Updating the "ray"
		self.ray.setLine(QLine(0, 0, distance*math.cos(self.car.angle), - distance*math.sin(self.car.angle)))

	def boundingRect(self):
		return QRectF(self.x(), self.y(), self.image.boundingRect().width() , self.image.boundingRect().height())

	def x(self):
		return self.pos().x()

	def y(self):
		return self.pos().y()

	def frontX(self):
		return self.x() + cos(self.car.angle) * self.img.width()
	def frontY(self):
		return self.y() - sin(self.car.angle) * self.img.width()

	def topLeftX(self):
		return self.x() - ( self.image.boundingRect().width() / 2 )

	def topLeftY(self):
		return self.y() - ( self.image.boundingRect().height() / 2 )

	# def mousePressEvent(self, event):
	# 	super(Car, self).mousePressEvent(event)
	# 	print "Car mouse event at ({} , {})".format(event.pos().x(), event.pos().y())

	# 	event.accept()




class GraphicsStaticCarItem(QGraphicsObject):
	"""
	'Static' view of the car (not affected by the car's movements)
	Used in the 'manual' interface
	"""
	default_width = 100
	default_length = 200

	def __init__(self, car, sprite_name = "sedan", shadow = True):
		super(GraphicsCarItem, self).__init__()

		pen = QPen()

		self.car = car
		self.car.addView(self)

		# Setting up text
		self.text = QGraphicsTextItem("", self)
		self.text.setFont(QFont("Ubuntu-L.ttf"))
		self.text.setPos(-140, -140)

		self.textShadow = QGraphicsDropShadowEffect()
		self.textShadow.setBlurRadius(3)
		self.textShadow.setColor( QColor(0, 0, 0) )
		self.textShadow.setOffset(1, 1)
		self.text.setGraphicsEffect( self.textShadow )

		self.text.setDefaultTextColor(QColor(210, 220, 250))
		self.text.font().setBold(True)

		# Initializing image
		self.sprite_name = sprite_name
		self.img = SPRITES[sprite_name]

		self.image = QGraphicsPixmapItem( QPixmap(SPRITES[sprite_name] ), self)
		self.image.setOffset(-self.img.width()/2, -self.img.height()/2)

		# Shadow effect on the car's image
		if shadow:
			self.shadow = QGraphicsDropShadowEffect()
			self.shadow.setBlurRadius(80)
			self.shadow.setColor( QColor(80, 90, 220) )
			self.shadow.setOffset(0, 0)
			self.image.setGraphicsEffect( self.shadow )

		# Initializing the "view ray"
		self.line = QLine(self.car.x, self.car.y, 0, 0)
		self.ray = QGraphicsLineItem(self.line, self )
		self.ray.setZValue(-1)

		pen.setColor(QColor(180, 200, 200))
		pen.setWidth(2)
		self.ray.setPen(pen)

		# Caching for the graphics
		self.setCacheMode( QGraphicsItem.ItemCoordinateCache )

		self.rect = QRectF()
		self.update()

	def setCaption(self, text):
		self.text.setPlainText(text)

	def paint(self, painter=None, style=None, widget=None):
		pass

	def update(self):
		super(GraphicsCarItem, self).update()

		# Rotating the car around its center
		if self.image.rotation() != self.car.angle:
			self.image.setRotation(-math.degrees(self.car.angle))

		self.setPos(self.car.x, self.car.y)

		#Updating the caption
		distance = 0
		if self.car.moving:
			self.setCaption( "Car moving... " )
		elif self.car.distance:
			self.setCaption( "Closest object at : {}".format(int(self.car.distance)) )
			distance = self.car.distance
		else:
			self.setCaption( "No object ahead" )

		# Updating the "ray"
		self.ray.setLine(QLine(0, 0, distance*math.cos(self.car.angle), - distance*math.sin(self.car.angle)))

	def boundingRect(self):
		return QRectF(self.x(), self.y(), self.image.boundingRect().width() , self.image.boundingRect().height())

	def x(self):
		return self.pos().x()

	def y(self):
		return self.pos().y()

	def frontX(self):
		return self.x() + cos(self.car.angle) * self.img.width()
	def frontY(self):
		return self.y() - sin(self.car.angle) * self.img.width()

	def topLeftX(self):
		return self.x() - ( self.image.boundingRect().width() / 2 )

	def topLeftY(self):
		return self.y() - ( self.image.boundingRect().height() / 2 )

	# def mousePressEvent(self, event):
	# 	super(Car, self).mousePressEvent(event)
	# 	print "Car mouse event at ({} , {})".format(event.pos().x(), event.pos().y())

	# 	event.accept()