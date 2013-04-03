"""
A heatmap module for visualizing probabilities calculus - WIP
"""
import random
from PySide import QtGui, QtCore

class ProbabilityCell(object):
    def __init__(self, x, y, probability = None):
        self.x = x
        self.y = y
        if probability is None:
            self.p = random.random()
        else:
            self.p = probability

class Heatmap(object):

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cells = set()

        self.randPopulate(100)

    def randPopulate(self, N):
        """
        Populates the heatmap randomly
        """
        for i in xrange(N):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.cells.add(ProbabilityCell(x, y))

class GraphicalHeatmap(QtGui.QGraphicsObject):

    def __init__(self, heatmap):
        super(GraphicalHeatmap, self).__init__()
        self.heatmap = heatmap

    def paint(self, painter=None, style=None, widget=None):

        self.painted = True
        pen = QtGui.QPen()
        pen.setColor(QtGui.QColor(0, 200, 0))
        pen.setWidth(10)
        painter.setPen(pen)

        for cell in self.heatmap.cells:
            color = QtGui.QColor.fromHsvF(cell.p / 3, 0.5, 0.8)
            painter.setPen( color )
            painter.setBrush( color )
            painter.drawEllipse(cell.x, cell.y, 10 + cell.p*20, 10 + cell.p*20)

    def boundingRect(self):
        return QtCore.QRectF(0, 0, self.heatmap.width, self.heatmap.height )