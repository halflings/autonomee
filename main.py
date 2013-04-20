#!/usr/bin/env python

from PySide import QtCore, QtGui

from manual import ManualView
from auto import AutoView


class MainWindow(QtGui.QMainWindow):
    AUTO_MODE = 0
    MANUAL_MODE = 1
    def __init__(self):
        super(MainWindow, self).__init__()

        self.currentPath = ''

        self.automaticView = AutoView()
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
        self.backgroundAction.setEnabled(True)
        self.backgroundAction.setCheckable(True)
        self.backgroundAction.setChecked(True)
        self.backgroundAction.toggled.connect(self.automaticView.setViewBackground)

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
        self.automaticView = AutoView()
        self.setWindowTitle("Carosif - Manual mode")

    def automaticMode(self):
        self.setCentralWidget(self.automaticView)
        self.manualView = ManualView()
        self.setWindowTitle("Carosif - Automatic mode")

    def openFile(self, path=None):
        if not path:
            path = QtGui.QFileDialog.getOpenFileName(self, "Open SVG File", self.currentPath, "SVG files (*.svg *.svgz *.svg.gz)")[0]
        if path:
            svg_file = QtCore.QFile(path)
            if not svg_file.exists():
                QtGui.QMessageBox.critical(self, "Open SVG File",
                        "Could not open file '%s'." % path)
                self.backgroundAction.setEnabled(False)
                return

            self.automaticView.openFile(svg_file)
            if not path.startswith(':/'):
                self.currentPath = path
                self.setWindowTitle("Carosif - Automatic mode - Map : {}".format(self.currentPath))
            self.backgroundAction.setEnabled(True)

            self.resize(self.automaticView.sizeHint() + QtCore.QSize(80, 80 + self.menuBar().height()))

            #self.svg = pysvg.parser.parse('mapexample.svg')


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
