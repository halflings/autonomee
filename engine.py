# -*- coding: utf-8 -*-

"""
    engine.py - all what's related to the car's model (coordinates, heading angle, ...)
"""


from PySide.QtCore import *

from math import cos, sin


class Car(QObject):

    max_temperature = 120.

    # TODO : Should be in mm
    def_width = 100
    def_length = 200

    # Noise parameters are in cm and degrees
    def_sensor = 5.
    def_displacement = 5.
    def_rotation = 5.

    def __init__(self, map=None, x=0, y=0, width=def_width, length=def_length):
        super(Car, self).__init__()

        # The map where the car is located
        self.map = map

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

        # Temperature is in Celcius degrees (float)
        self.temperature = 25.

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

    def setMoving(self, movingStatus):
        self.moving = movingStatus

        self.update()

    # Angle (in radians, from 0 to 2*pi)
    def readAngle(self):
        return self.angle

    def setAngle(self, angle):
        self.angle = angle

        self.update()

    angleProperty = Property(float, readAngle, setAngle)

    # Position (# TODO : should be in mm)
    def readPosition(self):
        return QPointF(self.x, self.y)

    def setPosition(self, position):
        self.x, self.y = position.x(), position.y()

    positionProperty = Property(QPointF, readPosition, setPosition)

    # Temperature (in celcius)
    def readTemperature(self):
        return self.temperature

    def setTemperature(self, temperature):
        self.temperature = temperature

    temperatureProperty = Property(float, readTemperature, setTemperature)

    def updateMap(self):
        self.map.setRadius(max(self.width, self.length))

    def update(self):
        # Calculating the distance to the closest object
        if self.map is not None and not self.moving:
            self.distance = self.map.rayDistance(self.x, self.y, self.angle)

        # TODO : Remove this, for testing  only
        self.temperature =  (self.temperature + 1) % 100
        self.speed = (self.speed + 1) % 180


        for view in self.views:
            view.update()

    def __repr__(self):
        return "Angle : {} | Position ({}, {}) | Distance : {}".format(self.angle, self.x, self.y, self.distance)

