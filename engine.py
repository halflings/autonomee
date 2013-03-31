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

		self.speed = 0
		self.distance = None
		self.caption = ""

		self.text = QtGui.QGraphicsTextItem("", self)
		self.text.setFont("Ubuntu Light")


		#Angle is in radian, and follows the traditional trigonometric orientation
		#			   pi/2
		#	pi or -pi __|__ 0
		#				|
		#			  -pi/2
		self.angle = 0

		# Initializing image
		self.sprite_name = sprite_name
		self.img = Car.sprites[sprite_name]

		# Initializing the "view ray"
		self.ray = None

		self.setPos(x, y)

		#print "Car width {} | Car length {} | Car sprite {}".format(self.width, self.length, self.sprite)

		#Some random flags ... (should be useful later)
		self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)
		self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)

		self.rect = QtCore.QRectF()
		self.update()

	def move(self, mov):

		dx = mov * cos(self.angle)
		dy = -mov * sin(self.angle)

		self.setPos( self.x() + dx , self.y() + dy )

		self.update()

	def rotate(self, angle):

		#Updating angle
		self.angle = angle

		transform = QtGui.QTransform()
		transform.rotate(-math.degrees(angle/2))

		self.img = Car.sprites[self.sprite_name].transformed(transform, QtCore.Qt.SmoothTransformation)

		self.img = self.img.transformed(transform)

		self.update()

	def setPos(self, x, y):
		super(Car, self).setPos(x, y)
		self.update()

	def paint(self, painter=None, style=None, widget=None):

		pen = QtGui.QPen()
		pen.setColor(QtGui.QColor(20, 124, 228))
		pen.setWidth(3)
		painter.setPen(pen)

		# Drawing the car's image
		painter.drawImage(self.topLeftX(), self.topLeftY(), self.img)

		#Car's front
		painter.drawRect(self.frontX()-1, self.frontY()-1, 1, 1)

		#Ray
		painter.drawLine(self.ray)

		#Car's center
		painter.drawRect(self.x() - 1, self.y() - 1, 1, 1)

	def update(self):
		super(Car, self).update()

		if self.map:
			self.distance = self.map.RayDistance(self.frontX(), self.frontY(), self.angle)

		if self.distance:
			self.caption = "Closest object at : {}".format(int(self.distance))
			distance = self.distance
		else:
			self.caption = "No object ahead"
			distance = 0

		#Updating the caption
		self.text.setPlainText(self.caption)

		self.ray = QtCore.QLine(self.frontX(), self.frontY(),
			self.frontX() + distance*math.cos(self.angle), self.frontY() - distance*math.sin(self.angle))

		self.prepareGeometryChange()

	def boundingRect(self):
		distance = 0
		if self.distance:
			distance = self.distance

		return QtCore.QRectF(self.topLeftX(), self.topLeftY(), self.img.width() + distance * 3 , self.img.height() + distance * 3)


	def x(self):
		return self.pos().x()

	def y(self):
		return self.pos().y()

	def frontX(self):
		return self.x() + cos(self.angle) * self.width

	def frontY(self):
		return self.y() - sin(self.angle) * self.width

	def topLeftX(self):
		return self.x() - ( self.img.width() / 2 )

	def topLeftY(self):
		return self.y() - ( self.img.height() / 2 )

	def formatAngle(self, angle):
		return (angle + math.pi)%(2*math.pi) - math.pi

	# def mousePressEvent(self, event):
	# 	super(Car, self).mousePressEvent(event)
	# 	print "Car mouse event at ({} , {})".format(event.pos().x(), event.pos().y())

	# 	event.accept()