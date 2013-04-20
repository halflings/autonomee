"""
    manual.py - The view shown when controlling the car manually.
"""

from PySide import QtGui
import engine
import math


class ManualView(QtGui.QGraphicsView):

    def __init__(self, parent=None):
        super(ManualView, self).__init__(parent)

        self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)

        self.setScene(ManualScene(self))

        tilePixmap = QtGui.QPixmap(64, 64)
        tilePixmap.fill(QtGui.QColor(230, 230, 230))
        self.setBackgroundBrush(QtGui.QBrush(tilePixmap))

    def paintEvent(self, event):
        super(ManualView, self).paintEvent(event)

class ManualScene(QtGui.QGraphicsScene):
    def __init__(self, parent=None):
        super(ManualScene, self).__init__(parent)

        # POUR LORIC : Ajoute ici les objets graphiques dont t'as besoin pour ta scene
        # Pour changer leur apparence, regarde tout ce qui est 'setPen', utilis&eacute; dans engine.py et ici

        # Ex1 un rectangle
        rect = QtGui.QGraphicsRectItem(10, 10, 200, 200)
        self.addItem( rect )

        # Ex2 une voiture
        self.car = engine.Car()
        self.car.setAngle(math.pi/2)
        self.addItem(self.car)

    def mousePressEvent(self, event):
        x, y = event.scenePos().x(), event.scenePos().y()

        super(ManualScene,self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        x, y = event.scenePos().x(), event.scenePos().y()
        super(ManualScene,self).mouseMoveEvent(event)
