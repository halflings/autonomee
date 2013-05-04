# -*- coding: utf-8 -*-

"""
    engine.py - all what's related to the car's model (coordinates, heading angle, ...)
"""


from PySide.QtCore import *

from math import cos, sin, pi, degrees


class Car(QObject):

    updateSignal = Signal(int)

    max_temperature = 120.

    # TODO : Should be in mm
    def_width = 100
    def_length = 200

    # A noise factor, determined empirically
    def_sensor = 100.

    # Noise in cm and degrees
    def_displacement = 5.
    def_rotation = 2.

    # Distance at which the car is 'in danger' (obstacle too close)
    danger_distance = 300

    def __init__(self, map=None, carSocket=None, x=0, y=0, width=def_width, length=def_length):
        super(Car, self).__init__()

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

        self.speed = 15

        # Noise parameters
        self.sensor_noise = Car.def_sensor
        self.displacement_noise = Car.def_displacement
        self.rotation_noise = Car.def_rotation

        # Distance to the closest object ahead
        self.distance = None

        # True when the car is moving :
        self.moving = False

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

    def move(self, speed):
        self.x += speed * cos(self.angle)
        self.y += speed * -sin(self.angle)

        # TODO: Temporary...
        # if self.socket.connected:
        #     # SET ANGLE : '01' + '#' + angle on 6 digits + '#' + distance on 6 digits
        #     self.socket.send( "01#{0:06d}#{1:06d}".format(int(degrees(self.angle)), int(speed)) )

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

    def notify(self, signal=1):
        self.updateSignal.emit(signal)

    def update(self, signal=1):
        # Calculating the distance to the closest object
        if self.map is not None and not self.moving:
            self.distance = self.map.rayDistance(self.x, self.y, self.angle)

        for view in self.views:
            view.update()

    def __repr__(self):
        return "Angle : {} | Position ({}, {}) | Distance : {}".format(self.angle, self.x, self.y, self.distance)

