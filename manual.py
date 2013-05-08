# -*- coding: utf8 -*-

"""
    manual.py - The view shown when controlling the car manually.
"""

from PySide.QtGui import *
from PySide.QtCore import *

import widgets


class ManualView(QGraphicsView):

    def __init__(self, car, parent=None):
        super(ManualView, self).__init__(parent)

        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        scene = ManualScene(car=car, parent=self)
        self.setScene(scene)

        # Disabling scrollbars
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def showEvent(self, event):
        super(ManualView, self).showEvent(event)

    def paintEvent(self, event):
        super(ManualView, self).paintEvent(event)


class ManualScene(QGraphicsScene):

    def __init__(self, car, parent=None):
        super(ManualScene, self).__init__(parent)

        self.car = car

        # Gradient background
        self.gradient = QLinearGradient(0, -200, 0, 600)
        lightGray = 0.1
        darkGray = 0.03
        self.gradient.setColorAt(0, QColor.fromRgbF(darkGray, darkGray, darkGray, 1))
        self.gradient.setColorAt(1, QColor.fromRgbF(lightGray, lightGray, lightGray, 1))
        self.setBackgroundBrush(self.gradient)

        self.w = 980
        self.h = 700

        # Rect
        self.rectItem = QGraphicsRectItem(0, 0, self.w, self.h)
        self.rectItem.setPen(QColor.fromRgbF(1., 0., 0., 0.))
        self.rectItem.setFlags(QGraphicsItem.ItemClipsToShape)
        self.rectItem.setZValue(0)
        self.addItem(self.rectItem)

        # Text
        self.titleItem = QGraphicsTextItem("Manual mode")
        self.titleItem.setFont(QFont("Ubuntu-L.ttf", 35, QFont.Light))
        # 'Dirty' centering of the text
        self.titleItem.setPos(100 + (self.w - self.titleItem.boundingRect().width())/2, 10)
        self.titleItem.setDefaultTextColor(QColor(210, 220, 250))
        self.addItem(self.titleItem)

        # Compass
        self.compass = widgets.CarCompass(self.car)
        self.compass.setPos(50, self.h - self.compass.boundingRect().height())
        self.addItem(self.compass)

        # Speed meter
        self.speedmeter = widgets.CarSpeedMeter(self.car)
        x = self.compass.pos().x() + self.compass.boundingRect().width() + 40
        y = self.h - self.speedmeter.boundingRect().height() - 120
        self.speedmeter.setPos(x, y)
        self.addItem(self.speedmeter)

        # Thermometer
        self.thermometer = widgets.CarThermometer(self.car)
        x = self.speedmeter.pos().x() + self.speedmeter.boundingRect().width() + 40
        y = self.h - self.thermometer.boundingRect().height()
        self.thermometer.setPos(x, y)
        self.addItem(self.thermometer)

        # "Obstacle warner"
        self.obstacleWarning = widgets.ObstacleWarning(self.car)
        self.addItem(self.obstacleWarning)

        # List of pressed keys (to press multiple keys at the same time)
        self.keylist = list()

        self.firstrelease = True

    def mousePressEvent(self, event):
        x, y = event.scenePos().x(), event.scenePos().y()

        super(ManualScene, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        x, y = event.scenePos().x(), event.scenePos().y()
        super(ManualScene, self).mouseMoveEvent(event)

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_L:
            servoAngle = min(80, self.car.servoAngle + 10)
            self.car.setServoAngle(servoAngle)
        if event.key() == Qt.Key_J:
            servoAngle = max(-80, self.car.servoAngle - 10)
            self.car.setServoAngle(servoAngle)

    def processmultikeys(self,keyspressed):
        print keyspressed
