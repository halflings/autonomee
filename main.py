#!/usr/bin/env python

# This is only needed for Python v2 but is harmless for Python v3.
# import sip
# sip.setapi('QString', 2)

from PySide import QtCore, QtGui, QtSvg
import svg
import math

import engine

class MainWindow(QtGui.QMainWindow):
    AUTO_MODE = 0
    MANUAL_MODE = 1
    def __init__(self):
        super(MainWindow, self).__init__()

        self.currentPath = ''

        self.view = SvgView()
        self.manualView = ManualView()

        # File menu
        fileMenu = QtGui.QMenu("&File", self)
        openAction = fileMenu.addAction("&Open...")
        openAction.setShortcut("Ctrl+O")
        quitAction = fileMenu.addAction("E&xit")
        quitAction.setShortcut("Ctrl+Q")

        openAction.triggered.connect(self.openFile)
        quitAction.triggered.connect(QtGui.qApp.quit)

        self.menuBar().addMenu(fileMenu)

        # View menu
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

        # Mode menu
        modeMenu = QtGui.QMenu("&Mode", self)

        manualAction = modeMenu.addAction("M&anual")
        manualAction.setShortcut("Ctrl+M")
        manualAction.triggered.connect(self.manualMode)

        automaticAction = modeMenu.addAction("A&utomatic")
        automaticAction.setShortcut("Ctrl+A")
        automaticAction.triggered.connect(self.automaticMode)

        self.menuBar().addMenu(modeMenu)

        self.automaticMode()

    def manualMode(self):
        self.setCentralWidget(self.manualView)
        self.view = SvgView()
        self.setWindowTitle("Carosif - Manual mode")

    def automaticMode(self):
        self.setCentralWidget(self.view)
        self.manualView = SvgView()
        self.setWindowTitle("Carosif - Automatic mode")

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
                self.setWindowTitle("Carosif - Automatic mode - Map : {}".format(self.currentPath))
            self.outlineAction.setEnabled(False)
            self.backgroundAction.setEnabled(True)

            self.resize(self.view.sizeHint() + QtCore.QSize(80, 80 + self.menuBar().height()))

            #self.svg = pysvg.parser.parse('mapexample.svg')

class ManualView(QtGui.QGraphicsView):

    def __init__(self, parent=None):
        super(ManualView, self).__init__(parent)

        self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)

        self.renderer = SvgView.Native
        self.svgItem = None
        self.backgroundItem = None
        self.outlineItem = None
        self.image = QtGui.QImage()

        self.setScene(ManualScene(self))

        tilePixmap = QtGui.QPixmap(64, 64)
        tilePixmap.fill(QtGui.QColor(230, 230, 230))
        self.setBackgroundBrush(QtGui.QBrush(tilePixmap))

    def paintEvent(self, event):
        super(ManualView, self).paintEvent(event)

class ManualScene(QtGui.QGraphicsScene):
    def __init__(self, parent=None):
        super(ManualScene, self).__init__(parent)
        self.car = engine.Car()

    def mousePressEvent(self, event):
        x, y = event.scenePos().x(), event.scenePos().y()

        super(ManualScene,self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        x, y = event.scenePos().x(), event.scenePos().y()
        super(ManualScene,self).mouseMoveEvent(event)

class ViewerScene(QtGui.QGraphicsScene):
    def __init__(self, parent=None):
        super(ViewerScene, self).__init__(parent)
        #self.setDragMode(QtGui.QGraphicsScene.ScrollHandDrag)

        self.x = 0
        self.y =0

        self.car = None
        self.map = None

        self.path = None
        self.ray = None

        self.line = None
    def mousePressEvent(self, event):
        x, y = event.scenePos().x(), event.scenePos().y()
        if not self.car:
            self.car = engine.Car(self.map, x, y)
            self.addItem(self.car)
        else:
            self.path = self.map.search((self.car.x, self.car.y), (x,y))
            i = 0
            line = QtGui.QGraphicsLineItem(self.path[i].x, self.path[i].y, self.path[i+1].x, self.path[i+1].y)
            # if self.line is None:
            #     self.line = line
            #     self.addItem(self.line)
            # else:
            #     self.line = line

            if self.path is not None:
                for i in range(len(self.path)-1):
                    self.addItem( QtGui.QGraphicsLineItem(self.path[i].x, self.path[i].y, self.path[i+1].x, self.path[i+1].y))


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

    # def paintEvent(self, event):
    #     if self.path is not None:
    #         for i in range(len(self.path)-1):
    #             painter.drawLine(self.path[i].x, self.path[i].y, self.path[i+1].x, self.path[i+1].y)

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
        outline = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.DashDotLine)
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