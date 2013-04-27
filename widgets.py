# -*- coding: utf8 -*-

"""
    widgets.py - Many custom graphic items (Qt) used -mainly- to visualize the car
"""
from PySide.QtCore import *
from PySide.QtGui import *

import math
from engine import Car


class InfoBox(QGraphicsObject):

    """
    A (rounded border, and translucide) rectangle containg some information
    """

    padding = 10

    def __init__(self, text="No text", fontsize=20, capitalize=True):
        super(InfoBox, self).__init__()

        if capitalize:
            text = text.upper()

        # Setting up text
        self.text = QGraphicsTextItem(text, self)
        self.font = QFont("Ubuntu", fontsize)
        self.text.setFont(self.font)
        self.text.setDefaultTextColor(QColor(255, 255, 255))

        self.text.setPos(InfoBox.padding, InfoBox.padding)

        self.textShadow = QGraphicsDropShadowEffect()
        self.textShadow.setBlurRadius(3)
        self.textShadow.setColor(QColor(0, 0, 0))
        self.textShadow.setOffset(1, 1)
        self.text.setGraphicsEffect(self.textShadow)

        # Background
        boxW = self.text.boundingRect().width() + 2*InfoBox.padding
        boxH = self.text.boundingRect().height() + 2*InfoBox.padding
        self.background = QGraphicsRectItem(0, 0, boxW, boxH, parent=self)
        self.background.setOpacity(0.5)
        self.background.setBrush(QColor(255, 255, 255))
        self.background.setZValue(-1)

        # Shadow effect on the background
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(1)
        self.shadow.setColor(QColor(0, 0, 0))
        self.shadow.setOffset(1, 1)
        self.background.setGraphicsEffect(self.shadow)

        # Caching
        self.setCacheMode(QGraphicsItem.ItemCoordinateCache)

        self.update()

    def paint(self, painter=None, style=None, widget=None):
        pass

    def setCaption(self, text):
        self.text.setPlainText(text)
        w = self.text.boundingRect().width() + 2 * InfoBox.padding
        h = self.text.boundingRect().height() + 2 * InfoBox.padding
        self.background.setRect(QRect(0, 0, w, h, parent=self))
        self.update()

    def boundingRect(self):
        return self.background.boundingRect()


class GraphicsCarItem(QGraphicsObject):

    """
    A dynamic graphical representation of a car.
    Received an update signal (update() method) when the model is modified
    """

    # TODO : scaling should be dynamic (according to the car's width )
    default_image = QImage("img/car.png")

    # In the view, everything should be expressed in px (converted from the
    # model where mm should be used)
    default_width = 200
    default_length = 200
    scale_factor = 0.5

    def __init__(self, car, width=default_width, shadow=True):
        super(GraphicsCarItem, self).__init__()

        pen = QPen()

        self.car = car
        self.car.addView(self)

        # TODO : add conversion
        self.w = self.car.length

        # Setting up text
        self.text = QGraphicsTextItem("", self)
        self.text.setFont(QFont("Ubuntu"))
        self.text.setPos(-140, -140)

        self.textShadow = QGraphicsDropShadowEffect()
        self.textShadow.setBlurRadius(3)
        self.textShadow.setColor(QColor(0, 0, 0))
        self.textShadow.setOffset(1, 1)
        self.text.setGraphicsEffect(self.textShadow)

        self.text.setDefaultTextColor(QColor(210, 220, 250))
        self.text.font().setBold(True)

        # Initializing image
        self.img = GraphicsCarItem.default_image.scaledToWidth(self.w)

        self.image = QGraphicsPixmapItem(QPixmap(self.img), self)
        self.image.setOffset(-self.img.width()/2, -self.img.height()/2)

        # Shadow effect on the car's image
        if shadow:
            self.shadow = QGraphicsDropShadowEffect()
            self.shadow.setBlurRadius(80)
            self.shadow.setColor(QColor(80, 90, 220))
            self.shadow.setOffset(0, 0)
            self.image.setGraphicsEffect(self.shadow)

        # Initializing the "view ray"
        self.line = QLine(self.car.x, self.car.y, 0, 0)
        self.ray = QGraphicsLineItem(self.line, self)
        self.ray.setZValue(-1)

        pen.setColor(QColor(180, 200, 200))
        pen.setWidth(2)
        self.ray.setPen(pen)

        # Caching
        self.setCacheMode(QGraphicsItem.ItemCoordinateCache)

        self.update()

    def __del__(self):
        self.car.removeView(self)

    def setCaption(self, text):
        self.text.setPlainText(text)

    def paint(self, painter=None, style=None, widget=None):
        pass

    def update(self):
        super(GraphicsCarItem, self).update()

        # Rotating the car around its center
        if self.image.rotation() != self.car.angle:
            self.image.setRotation(-math.degrees(self.car.angle))

        if self.w != self.car.length:
            self.w = self.car.length
            self.img = GraphicsCarItem.default_image.scaledToWidth(self.w)
            self.image.setPixmap( QPixmap(self.img) )
            self.image.setOffset(-self.img.width()/2, -self.img.height()/2)

        self.setPos(self.car.x, self.car.y)

        # Updating the caption
        distance = 0
        if self.car.moving:
            self.setCaption("Car moving... ")
        elif self.car.distance:
            self.setCaption("Closest object at : {}".format(int(self.car.distance)))
            distance = self.car.distance
        else:
            self.setCaption("No object ahead")

        # Updating the "ray"
        line = QLine(0, 0, distance*math.cos(self.car.angle), - distance*math.sin(self.car.angle))
        self.ray.setLine(line)

    def boundingRect(self):
        return QRectF(self.x(), self.y(), self.image.boundingRect().width(), self.image.boundingRect().height())

    def x(self):
        return self.pos().x()

    def y(self):
        return self.pos().y()

    def topLeftX(self):
        return self.x() - (self.image.boundingRect().width() / 2)

    def topLeftY(self):
        return self.y() - (self.image.boundingRect().height() / 2)

    # def mousePressEvent(self, event):
    #   super(Car, self).mousePressEvent(event)
    # print "Car mouse event at ({} , {})".format(event.pos().x(),
    # event.pos().y())

    #   event.accept()


class CarCompass(QGraphicsObject):

    background = QImage("img/dashboard/compass.png")
    arrow = QImage("img/dashboard/compassArrow.png")

    orientations = ["NE", "SE", "SW", "NW"]

    """ A compass showing the car's current orientation """

    def __init__(self, car):
        super(CarCompass, self).__init__()

        self.car = car
        self.car.addView(self)

        # Compass's background
        self.background = QGraphicsPixmapItem(QPixmap(CarCompass.background), self)

        # Shadow effect on the compass
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(100)
        self.shadow.setColor(QColor(80, 80, 80))
        self.shadow.setOffset(0, 0)
        self.background.setGraphicsEffect(self.shadow)

        # Compass's needle
        self.needle = QGraphicsPixmapItem(QPixmap(CarCompass.arrow), self)
        self.needle.setOffset(-CarCompass.arrow.width()/2, -CarCompass.arrow.height()/2)
        self.needle.setPos(CarCompass.background.width()/2, CarCompass.background.height()/2)

        # Info box
        self.infobox = InfoBox(fontsize=15)
        self.infobox.setParentItem(self)

        # Caching
        self.setCacheMode(QGraphicsItem.ItemCoordinateCache)

        self.update()



    def paint(self, painter=None, style=None, widget=None):
        pass

    def update(self):
        super(CarCompass, self).update()

        # Rotating the NEEDLE around its center
        if self.needle.rotation() != self.car.angle:
            self.needle.setRotation(math.degrees(self.car.angle))

        # Updating the info box
        orientation = int(math.degrees(self.car.angle) / 90)
        self.infobox.setCaption("{0} | {1:.2f}°".format(CarCompass.orientations[orientation], math.degrees(self.car.angle)))
        x = (self.boundingRect().width() - self.infobox.boundingRect().width()) / 2
        y = self.boundingRect().height() + 20
        self.infobox.setPos(x, y)

        # #DEBUG RECT
        # self.rect = QGraphicsRectItem(self.infobox.boundingRect(), parent=self)
        # self.rect.setPen(QColor(255, 0, 0))

    def boundingRect(self):
        return self.background.boundingRect().united(self.infobox.boundingRect())


class CarThermometer(QGraphicsObject):

    """ A thermometer showing the car's current temperature """

    background_empty = QImage("img/dashboard/thermometer-empty.png")
    background_full = QImage("img/dashboard/thermometer-full.png")

    def __init__(self, car):
        super(CarThermometer, self).__init__()

        self.car = car
        self.car.addView(self)

        # Initializing image

        # Background: an empty thermometer
        self.empty = QGraphicsPixmapItem(QPixmap(CarThermometer.background_empty), self)

        # Foreground: a full thermometer (that we'll crop according to the temperature)
        self.full = QGraphicsPixmapItem(QPixmap(CarThermometer.background_full), self)

        # Shadow effect on the thermometer
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(100)
        self.shadow.setColor(QColor(80, 80, 80))
        self.shadow.setOffset(0, 0)
        self.empty.setGraphicsEffect(self.shadow)

        # Info box
        self.infobox = InfoBox()
        self.infobox.setParentItem(self)

        # Caching
        self.setCacheMode(QGraphicsItem.ItemCoordinateCache)

        self.update()

    def paint(self, painter=None, style=None, widget=None):
        pass

    def update(self):
        super(CarThermometer, self).update()

        # Updating the 'full' thermometer's height
        y = max(0,  CarThermometer.background_full.height()*(1 - self.car.temperature / Car.max_temperature) - 130)
        y = min(y, CarThermometer.background_full.height())
        newImage = CarThermometer.background_full.copy(
            0, y, CarThermometer.background_full.width(), CarThermometer.background_full.height())

        self.full.setPixmap(QPixmap(newImage))
        self.full.setPos(0, y)

        # Updating the info box
        self.infobox.setCaption("{}°".format(self.car.temperature))
        self.infobox.setPos(self.empty.boundingRect().width() + 10, y)

    def boundingRect(self):
        return self.empty.boundingRect().united(self.infobox.boundingRect())


class CarSpeedMeter(QGraphicsObject):

    background = QImage("img/dashboard/speedmeter.png")
    centerwheel = QImage("img/dashboard/centerwheel.png")
    arrow = QImage("img/dashboard/speed-arrow.png")

    zeroAngle = -34.7
    anglePerCmS = 1.22
    maxSpeed = 220

    """ A compass showing the car's current orientation """

    def __init__(self, car):
        super(CarSpeedMeter, self).__init__()

        self.car = car
        self.car.addView(self)

        # Speed meter's background
        self.background = QGraphicsPixmapItem(QPixmap(CarSpeedMeter.background), self)

        # Shadow effect on the speedmeter
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(100)
        self.shadow.setColor(QColor(80, 80, 80))
        self.shadow.setOffset(0, 0)
        self.background.setGraphicsEffect(self.shadow)

        # Speed meter's arrow
        self.arrow = QGraphicsPixmapItem(QPixmap(CarSpeedMeter.arrow), self)
        self.arrow.setOffset(-CarSpeedMeter.arrow.width(), -CarSpeedMeter.arrow.height()/2)
        self.arrow.setPos(CarSpeedMeter.background.width()/2, CarSpeedMeter.background.height()/2)

        # Speed meter's arrow
        self.centerwheel = QGraphicsPixmapItem(QPixmap(CarSpeedMeter.centerwheel), self)
        self.centerwheel.setOffset(-CarSpeedMeter.centerwheel.width()/2, -CarSpeedMeter.centerwheel.height()/2)
        self.centerwheel.setPos(CarSpeedMeter.background.width()/2, CarSpeedMeter.background.height()/2)

        # Info box
        self.infobox = InfoBox(fontsize=22)
        self.infobox.setParentItem(self)

        # Caching the graphics
        self.setCacheMode(QGraphicsItem.ItemCoordinateCache)

        self.update()

    def paint(self, painter=None, style=None, widget=None):
        pass

    def update(self):
        super(CarSpeedMeter, self).update()

        # Rotating the SPEED ARROW around its center
        self.arrow.setRotation(CarSpeedMeter.zeroAngle + self.car.speed * CarSpeedMeter.anglePerCmS)

        # Updating the info box
        self.infobox.setCaption("{} cm/s".format(self.car.speed))
        x = (self.boundingRect().width() - self.infobox.boundingRect().width()) / 2
        y = 330
        self.infobox.setPos(x, y)

    def boundingRect(self):
        return self.background.boundingRect().united(self.infobox.boundingRect())

class GraphicalParticleFilter(QGraphicsObject):

    def __init__(self, partFilter):
        super(GraphicalParticleFilter, self).__init__()
        self.setCacheMode( QGraphicsItem.ItemCoordinateCache )
        self.particleFilter = partFilter

    def move(self, distance, angle = 0.):
        self.particleFilter.move(distance, angle)

    def sense(self, measuredDistance, angle):
        self.particleFilter.sense(measuredDistance, angle)

    def resample(self):
        self.particleFilter.resample()

    def normalize(self):
        self.particleFilter.normalize()

    def setMap(self, map):
        self.particleFilter.setMap(map)

    def paint(self, painter=None, style=None, widget=None):

        if self.particleFilter.map is not None:
            pen = QPen()
            pen.setColor(QColor(0, 200, 0))
            pen.setWidth(10)
            painter.setPen(pen)

            for particle in self.particleFilter.particles:
                color = QColor.fromHsvF(particle.p / 3, 0.5, 0.8, 0.5)
                painter.setPen( color )
                painter.setBrush( color )

                radius = 10 + particle.p*20

                painter.drawEllipse(particle.x, particle.y, radius, radius)

    def boundingRect(self):
        return QRectF(0, 0, self.particleFilter.width, self.particleFilter.height )