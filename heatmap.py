"""
A heatmap module for visualizing probabilities calculus - WIP
"""
import random
from PySide import QtGui, QtCore

class Heatmap(object):


    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [ [0 for x in range(self.width)] for y in range(self.height) ]

        self.randPopulate()

    def randPopulate(self):
        """
        Populates the heatmap randomly
        """
        for x in range(self.width):
            for y in range(self.height):
                self.grid[y][x] = random.random()


class GraphicalHeatmap(QtGui.QGraphicsItem):


    def __init__(self, heatmap, vw, vh):
        super(GraphicalHeatmap, self).__init__()
        self.heatmap = heatmap

        self.viewWidth = vw
        self.viewHeight = vh


    def paint(self, painter=None, style=None, widget=None):

        self.painted = True
        pen = QtGui.QPen()
        pen.setColor(QtGui.QColor(0, 200, 0))
        pen.setWidth(2)
        painter.setPen(pen)

        for j in range(self.heatmap.width):
            for i in range(self.heatmap.height):
                x = int( ( (j + 0.5)/self.heatmap.height ) * self.viewHeight )
                y = int( ( (i + 0.5)/self.heatmap.width ) * self.viewWidth )
                color = QtGui.QColor.fromHsvF(self.heatmap.grid[i][j] / 3, 0.7, 1 - self.heatmap.grid[i][j] / 2)
                pen.setColor( color )
                painter.setPen(pen)
                painter.drawRect(x, y, 2, 2)

    def boundingRect(self):
        return QtCore.QRectF(0, 0, self.viewWidth, self.viewHeight )