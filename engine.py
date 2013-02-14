from PySide import QtCore, QtGui
import math

class Car(QtGui.QGraphicsItem):
	#"ALL measurements must be in mm"
	# NOTE : The mm/px conversion should be done in the model ... maybe this class should do everything in px ...
	default_width = 100
	default_length = 200

	default_image =  QtGui.QImage("img/car.png")
	scale_factor = 0.5
	sprites = {"sedan" : default_image.scaledToWidth(default_image.width()*scale_factor)}

	def __init__(self, map, x=0, y=0, width = default_width, length = default_length, sprite_name = "sedan"):
		#QGraphicsItem's constructor
		super(Car, self).__init__()

		#The map where the car is located
		self.map = map
		#This should be in the map, but keep it here for test purpose :s

		#Model related attributes
		self.width = width
		self.length = length
		self.x = x
		self.y = y
		self.speed = 0
		self.distance = None
		self.caption = ""

		#Angle is in radian, and follows the traditional trigonometric orientation
		#			   pi/2
		#	pi or -pi __|__ 0
		#				|
		#			  -pi/2
		self.angle = 0

		# Initializing image
		self.sprite_name = sprite_name
		self.img = Car.sprites[sprite_name]

		#print "Car width {} | Car length {} | Car sprite {}".format(self.width, self.length, self.sprite)

		#Some random flags ...
		self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)
		self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)

		self.rect = QtCore.QRectF()
		self.updateBounding()


	def setPos(self, x, y):
		self.x = x
		self.y = y
		self.updateBounding()

	def move(self, mov):

		# if self.distance and self.distance < 100:
		# 	rightAngle, leftAngle = self.formatAngle(self.angle -0.5), self.formatAngle(self.angle + 0.5)

		# 	rightDistance = self.map.RayDistance(self.frontX(), self.frontY(), rightAngle)
		# 	leftDistance = self.map.RayDistance(self.frontX(), self.frontY(), leftAngle)

		# 	if rightDistance < leftDistance:
		# 		self.angle = leftAngle
		# 	else:
		# 		self.angle = rightAngle

		# 	self.rotate(self.angle)

		dx = mov*math.cos(self.angle)
		dy = -mov*math.sin(self.angle)

		#Make sure the car is still in the map
		#if int(self.x+dx) in xrange(self.map.width) and int(self.y+dy) in xrange(self.map.height):
		self.x += dx
		self.y += dy

		distance = self.map.RayDistance(self.x, self.y, self.angle)

		if distance:
			self.caption = "Closest object at : {}".format(int(distance))

		self.update()

	def rotate(self, angle):
		#Updating angle
		self.angle = angle

		transform = QtGui.QTransform()
		transform.rotate(-math.degrees(angle/2))

		self.img = Car.sprites[self.sprite_name].transformed(transform, QtCore.Qt.SmoothTransformation)


		self.img = self.img.transformed(transform)

		self.update()

		# print "New angle : {}".format(self.angle)

	def paint(self, painter=None, style=None, widget=None):
			pen = QtGui.QPen()
			pen.setColor(QtGui.QColor(20, 124, 228))
			pen.setWidth(3)
			painter.setPen(pen)

			painter.drawImage(self.topLeftX(), self.topLeftY(), self.img)


			#FOR DEBUG ONLY
			if self.distance:
				distance = self.distance
			else:
				distance = 300

			#Car's front
			painter.drawRect(self.frontX()-1, self.frontY()-1, 1, 1)

			painter.drawLine(self.frontX(), self.frontY(), self.frontX() + distance*math.cos(self.angle), self.frontY() - distance*math.sin(self.angle))
			painter.setFont(QtGui.QFont('Decorative', 10))
			painter.drawText(self.rect, QtCore.Qt.AlignLeft, self.caption)

			#Car's center
			painter.drawRect(self.x-1, self.y-1, 1, 1)

	def boundingRect(self):
		#print self.topLeftX(), self.topLeftY()
		return self.rect


	def update(self):
		self.distance = self.map.RayDistance(self.frontX(), self.frontY(), self.angle)

		if self.distance:
			self.caption = "Closest object at : {}".format(int(self.distance))
		else:
			self.caption = "No object ahead"

		self.updateBounding()

	def updateBounding(self):

		self.rect = QtCore.QRectF(self.topLeftX(), self.topLeftY(), self.img.width()*1.5, self.img.height()*1.5)

		self.prepareGeometryChange()

	def frontX(self):
		return self.x + math.cos(self.angle)*self.width

	def frontY(self):
		return self.y - math.sin(self.angle)*self.width

	def topLeftX(self):
		return self.x-self.img.width()/2

	def topLeftY(self):
		return self.y -self.img.height()/2

	def formatAngle(self, angle):
		return (angle + math.pi)%(2*math.pi) - math.pi

	# def mousePressEvent(self, event):
	# 	super(Car, self).mousePressEvent(event)
	# 	print "Car mouse event at ({} , {})".format(event.pos().x(), event.pos().y())

	# 	event.accept()