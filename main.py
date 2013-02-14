#!/usr/bin/env python

# This is only needed for Python v2 but is harmless for Python v3.
# import sip
# sip.setapi('QString', 2)

from PySide import QtCore, QtGui, QtSvg
import svg
import math

import engine

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.currentPath = ''

        self.view = SvgView()

        fileMenu = QtGui.QMenu("&File", self)
        openAction = fileMenu.addAction("&Open...")
        openAction.setShortcut("Ctrl+O")
        quitAction = fileMenu.addAction("E&xit")
        quitAction.setShortcut("Ctrl+Q")

        self.menuBar().addMenu(fileMenu)

        viewMenu = QtGui.QMenu("&View", self)
        self.backgroundAction = viewMenu.addAction("&Background")
        self.backgroundAction.setEnabled(False)
        self.backgroundAction.setCheckable(True)
        self.backgroundAction.setChecked(False)
        self.backgroundAction.toggled.connect(self.view.setViewBackground)

        self.outlineAction = viewMenu.addAction("&Outline")
        self.outlineAction.setEnabled(False)
        self.outlineAction.setCheckable(True)
        self.outlineAction.setChecked(True)
        self.outlineAction.toggled.connect(self.view.setViewOutline)

        self.menuBar().addMenu(viewMenu)

        openAction.triggered.connect(self.openFile)
        quitAction.triggered.connect(QtGui.qApp.quit)

        self.setCentralWidget(self.view)
        self.setWindowTitle("SVG Viewer")

    def openFile(self, path=None):
        if not path:
            path = QtGui.QFileDialog.getOpenFileName(self, "Open SVG File", self.currentPath, "SVG files (*.svg *.svgz *.svg.gz)")[0]
        if path:
            svg_file = QtCore.QFile(path)
            if not svg_file.exists():
                QtGui.QMessageBox.critical(self, "Open SVG File",
                        "Could not open file '%s'." % path)

                self.outlineAction.setEnabled(False)
                self.backgroundAction.setEnabled(False)
                return

            self.view.openFile(svg_file)
            if not path.startswith(':/'):
                self.currentPath = path
                self.setWindowTitle("%s - SVGViewer" % self.currentPath)
            self.outlineAction.setEnabled(False)
            self.backgroundAction.setEnabled(True)

            self.resize(self.view.sizeHint() + QtCore.QSize(80, 80 + self.menuBar().height()))

            #self.svg = pysvg.parser.parse('mapexample.svg')

class ExGraphicsItem (QtGui.QGraphicsItem):
    def __init__ (self, position):
        super(ExGraphicsItem, self).__init__()
        x = position.x()
        y = position.y()
        self.rectF = QtCore.QRectF(x,y,5,5)

        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)

    def boundingRect (self):
        return self.rectF
    def paint (self, painter=None, style=None, widget=None):
        painter.fillRect(self.rectF, QtCore.Qt.red)

    # def mouseMoveEvent(self, event):
    #     QtGui.QGraphicsItem.mouseMoveEvent(self, event)
    #     print event.scenePos().x()

class ViewerScene(QtGui.QGraphicsScene):
    def __init__(self, parent=None):
        super(ViewerScene, self).__init__(parent)
        #self.setDragMode(QtGui.QGraphicsScene.ScrollHandDrag)

        self.x = 0
        self.y =0

        self.car = None
        self.map = None
    def mousePressEvent(self, event):
        x, y = event.scenePos().x(), event.scenePos().y()
        if not self.car:
            self.car = engine.Car(self.map, x, y)
            self.addItem(self.car)

        super(ViewerScene,self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        x, y = event.scenePos().x(), event.scenePos().y()
        if self.car:
            #We calculate the angle (in radians) and convert it to the trigonometric referential
            angle = math.pi - math.atan2(self.car.y-y, self.car.x-x)
            if angle > math.pi:
                angle = angle - 2*math.pi

            self.car.rotate(angle)

    def keyPressEvent(self, event):
        speed = 20
        if self.car:
            if event.key()==QtCore.Qt.Key_Up or event.key()==QtCore.Qt.Key_Z:
                self.car.move(speed)
            elif event.key()==QtCore.Qt.Key_Down or event.key()==QtCore.Qt.Key_S:
                self.car.move(-speed)

    # def mouseMoveEvent(self, event):
    #     print "in mouse move"
    #     print event.scenePos().x()
    #     super(ViewerScene, self).mouseMoveEvent(event)


class SvgView(QtGui.QGraphicsView):
    Native, OpenGL, Image = range(3)

    def __init__(self, parent=None):
        super(SvgView, self).__init__(parent)

        self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)

        self.renderer = SvgView.Native
        self.svgItem = None
        self.backgroundItem = None
        self.outlineItem = None
        self.image = QtGui.QImage()

        self.setScene(ViewerScene(self))
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)

        # Prepare background check-board pattern.
        # tilePixmap = QtGui.QPixmap(64, 64)
        # tilePixmap.fill(QtCore.Qt.white)
        # tilePainter = QtGui.QPainter(tilePixmap)
        # color = QtGui.QColor(220, 220, 220)
        # tilePainter.fillRect(0, 0, 32, 32, color)
        # tilePainter.fillRect(32, 32, 32, 32, color)
        # tilePainter.end()

        tilePixmap = QtGui.QPixmap(1, 1)
        tilePixmap.fill(QtCore.Qt.white)
        self.setBackgroundBrush(QtGui.QBrush(tilePixmap))

    def drawBackground(self, p, rect):
        p.save()
        p.resetTransform()
        p.drawTiledPixmap(self.viewport().rect(),
                self.backgroundBrush().texture())
        p.restore()

    def openFile(self, svg_file):
        if not svg_file.exists():
            return

        s = self.scene()

        #Reset the zoom factor
        self.factor = 1
        #Reset the car
        s.car = None
        #Recreate a map tree by parsing the SVG
        s.map = svg.SvgTree(svg_file.fileName())

        if self.backgroundItem:
            drawBackground = self.backgroundItem.isVisible()
        else:
            drawBackground = False

        if self.outlineItem:
            drawOutline = self.outlineItem.isVisible()
        else:
            drawOutline = True

        s.clear()
        self.resetTransform()

        self.svgItem = QtSvg.QGraphicsSvgItem(svg_file.fileName())
        self.svgItem.setFlags(QtGui.QGraphicsItem.ItemClipsToShape)
        self.svgItem.setCacheMode(QtGui.QGraphicsItem.NoCache)
        self.svgItem.setZValue(0)


        self.backgroundItem = QtGui.QGraphicsRectItem(self.svgItem.boundingRect())
        self.backgroundItem.setBrush(QtCore.Qt.white)
        self.backgroundItem.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        self.backgroundItem.setVisible(drawBackground)
        self.backgroundItem.setZValue(-1)

        self.outlineItem = QtGui.QGraphicsRectItem(self.svgItem.boundingRect())
        outline = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.DashLine)
        outline.setCosmetic(True)
        self.outlineItem.setPen(outline)
        self.outlineItem.setBrush(QtGui.QBrush(QtCore.Qt.NoBrush))
        self.outlineItem.setVisible(drawOutline)
        self.outlineItem.setZValue(1)

        s.addItem(self.backgroundItem)
        s.addItem(self.svgItem)
        s.addItem(self.outlineItem)

        self.x = 0
        self.y = 0

        self.updateScene()

    def updateScene(self):
        self.scene().setSceneRect(self.outlineItem.boundingRect().adjusted(self.x-10, self.y-10, self.x+10, self.y+10))

    def setRenderer(self, renderer):
        self.renderer = renderer
        self.setViewport(QtGui.QWidget())

    def setViewBackground(self, enable):
        if self.backgroundItem:
            self.backgroundItem.setVisible(enable)

    def setViewOutline(self, enable):
        if self.outlineItem:
            self.outlineItem.setVisible(enable)

    def paintEvent(self, event):
        super(SvgView, self).paintEvent(event)

    def wheelEvent(self, event):
        factor = 1.2**(event.delta() / 240.0)

        self.scaleScene(factor)

        event.accept()

    def scaleScene(self, factor):
        self.factor *= factor
        self.scale(factor, factor)
        # self.svgItem.scale(factor, factor)
        # self.outlineItem.scale(factor, factor)
        # self.backgroundItem.scale(factor, factor)


if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)

    window = MainWindow()
    if len(sys.argv) == 2:
        window.openFile(sys.argv[1])
    else:
        window.openFile('maps/mapexample.svg')
    window.show()
    sys.exit(app.exec_())