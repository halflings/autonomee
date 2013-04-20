"""
    heatmap.py - a heatmap module for visualizing probabilities distribution
"""
from PySide import QtGui, QtCore

class GraphicalParticleFilter(QtGui.QGraphicsObject):

    def __init__(self, partFilter):
        super(GraphicalParticleFilter, self).__init__()
        self.setCacheMode( QtGui.QGraphicsItem.ItemCoordinateCache )
        self.particleFilter = partFilter

    def move(self, distance, angle):
        self.particleFilter.move(distance, angle)

    def sense(self, measuredDistance, angle):
        self.particleFilter(measuredDistance, angle)

    def resample(self):
        self.particleFilter.resample()

    def paint(self, painter=None, style=None, widget=None):

        self.painted = True
        pen = QtGui.QPen()
        pen.setColor(QtGui.QColor(0, 200, 0))
        pen.setWidth(10)
        painter.setPen(pen)

        for particle in self.particleFilter.particles:
            color = QtGui.QColor.fromHsvF(particle.p / 3, 0.5, 0.8, 0.5)
            painter.setPen( color )
            painter.setBrush( color )
            painter.drawEllipse(particle.x, particle.y, 10 + particle.p*20, 10 + particle.p*20)

    def boundingRect(self):
        return QtCore.QRectF(0, 0, self.heatmap.width, self.heatmap.height )