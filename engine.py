1# -*- coding: utf-8 -*-

"""
    engine.py - all what's related to the car's model (coordinates, heading angle, ...)
"""


from PySide.QtCore import *
from math import cos, sin, pi, radians


class Car(QObject):
    Automatic, Manual = range(2)

    updateSignal = Signal(int)

    max_temperature = 60.

    # TODO : Should be in mm
    def_width = 50
    def_length = 100

    # A noise factor, determined empirically
    def_sensor = 100.

    # Noise in % (0-100) and degrees
    def_displacement = 10.
    def_rotation = 2.

    # Distance at which the car is 'in danger' (obstacle too close)
    danger_distance = 150

    def __init__(self, map=None, carSocket=None, x=0, y=0, width=def_width, length=def_length):
        super(Car, self).__init__()

        # By default, the car is in the 'automatic' mode
        self.mode = Car.Automatic

        # The map where the car is located
        self.map = map

        # TCP socket connecting the model to the (real) car
        self.socket = carSocket

        # A signal used to update the model (and its views), thread-safe
        self.updateSignal.connect(self.update)

        self.x = x
        self.y = y

        self.width = width
        self.length = length


        # Current speed
        self.speed = 0.

        # Maximum speed (0 - 250)
        self.maxspeed = 250

        # Noise parameters
        self.sensor_noise = Car.def_sensor
        self.displacement_noise = Car.def_displacement
        self.rotation_noise = Car.def_rotation

        # Distance to the closest object ahead
        self.distance = None

        # True when the car is moving :
        self.moving = False

        # True when the car has been localized :
        self.localized = False

        # Angles are in radians
        #      pi/2
        #   pi __|__ 0
        #        |
        #     3*pi/2
        self.angle = 0

        # Angle auquel se trouve le servomoteur (controllant le capteur)
        self.servoAngle = 0

        # Temperature is in Celcius degrees (float)
        self.temperature = 25.

        self.views = set()

    def addView(self, view):
        self.views.add(view)

    def setSocket(self, carSocket):
        self.socket = carSocket

    def removeView(self, view):
        if view in self.views:
            self.views.remove(view)

    def pxWidth(self):
        return max(1., self.width * self.map.pixel_per_mm)

    def pxLength(self):
        return max(1., self.length * self.map.pixel_per_mm)

    def move(self, speed):
        self.x += -speed * self.map.pixel_per_mm * sin(self.angle - radians(self.map.north_angle))
        self.y += -speed * self.map.pixel_per_mm * cos(self.angle - radians(self.map.north_angle))

        self.notify()

    def setMoving(self, movingStatus):
        self.moving = movingStatus
        self.notify()

    def setSpeed(self, speed):
        self.speed = speed
        self.notify()

    # Angle (in radians, from 0 to 2*pi)
    def readAngle(self):
        return self.angle

    def setAngle(self, angle):
        self.angle = angle % (2*pi)
        self.notify()

    angleProperty = Property(float, readAngle, setAngle)

    # Position (# TODO : should be in mm)
    def readPosition(self):
        return QPointF(self.x, self.y)

    def setPosition(self, position):
        self.x, self.y = position.x(), position.y()
        self.notify()

    positionProperty = Property(QPointF, readPosition, setPosition)

    # Temperature (in celcius)
    def readTemperature(self):
        return self.temperature
    
    def setTemperature(self, temperature):
        self.temperature = temperature

    temperatureProperty = Property(float, readTemperature, setTemperature)

    def updateMap(self):
        self.map.setRadius(max(self.width, self.length))

    def setServoAngle(self, servoAngle):
        self.servoAngle = servoAngle
        if self.socket.connected:
            self.socket.setServo(self.servoAngle)

    def setMaxSpeed(self, maxspeed):
        self.maxspeed = max(0, min(250, maxspeed))
        if self.socket.connected:
            self.socket.setMaxSpeed(self.maxspeed)


    def notify(self, signal=1):
        self.updateSignal.emit(signal)

    def update(self, signal=1):
        # Calculating the distance to the closest object
        if self.mode == Car.Automatic and self.map is not None and not self.moving:
            self.distance = self.map.rayDistance(self.x, self.y, self.angle)

        for view in self.views:
            view.update()

    def __repr__(self):
        return "Angle : {} | Position ({}, {}) | Distance : {}".format(self.angle, self.x, self.y, self.distance)

