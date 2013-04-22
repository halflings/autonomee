#!/usr/bin/env python

"""
    main.py - application entry point and the main window (opening files, menus, ...).
"""

from PySide import QtCore, QtGui
from PySide.QtCore import *
from PySide.QtGui import *

from manual import ManualView
from auto import AutoView


class MainWindow(QMainWindow):
    AUTO_MODE = 0
    MANUAL_MODE = 1
    def __init__(self):
        super(MainWindow, self).__init__()

        self.currentPath = ''

        # Setting the views
        self.automaticView = AutoView()
        self.manualView = ManualView()

        # File menu
        fileMenu = QMenu("&File", self)
        openAction = fileMenu.addAction("&Open...")
        openAction.setShortcut("Ctrl+O")
        quitAction = fileMenu.addAction("E&xit")
        quitAction.setShortcut("Ctrl+Q")

        openAction.triggered.connect(self.openFile)
        quitAction.triggered.connect(qApp.quit)

        self.menuBar().addMenu(fileMenu)

        # View menu
        viewMenu = QMenu("&View", self)
        self.backgroundAction = viewMenu.addAction("&Background")
        self.backgroundAction.setEnabled(True)
        self.backgroundAction.setCheckable(True)
        self.backgroundAction.setChecked(True)
        self.backgroundAction.toggled.connect(self.automaticView.setViewBackground)

        self.menuBar().addMenu(viewMenu)

        # Mode menu
        modeMenu = QMenu("&Mode", self)

        manualAction = modeMenu.addAction("M&anual")
        manualAction.setShortcut("Ctrl+M")
        manualAction.triggered.connect(self.manualMode)

        automaticAction = modeMenu.addAction("A&utomatic")
        automaticAction.setShortcut("Ctrl+A")
        automaticAction.triggered.connect(self.automaticMode)

        # Adding the menu
        self.menuBar().addMenu(modeMenu)

        # Stacked widget
        self.stackedWidget = QStackedWidget()
        self.stackedWidget.addWidget(self.automaticView)
        self.stackedWidget.addWidget(self.manualView)

        self.setCentralWidget(self.stackedWidget)

    def manualMode(self):
        self.stackedWidget.setCurrentWidget( self.manualView )
        self.setWindowTitle("Carosif - Manual mode")

    def automaticMode(self):
        self.stackedWidget.setCurrentWidget( self.automaticView )
        self.setWindowTitle("Carosif - Automatic mode")

    def openFile(self, path=None):
        if not path:
            path = QFileDialog.getOpenFileName(self, "Open SVG File", self.currentPath, "SVG files (*.svg *.svgz *.svg.gz)")[0]
        if path:
            svg_file = QFile(path)
            if not svg_file.exists():
                QMessageBox.critical(self, "Open SVG File",
                        "Could not open file '%s'." % path)
                self.backgroundAction.setEnabled(True)
                return

            self.automaticView.openFile(svg_file)
            if not path.startswith(':/'):
                self.currentPath = path
                self.setWindowTitle("Carosif - Automatic mode - Map : {}".format(self.currentPath))
            self.backgroundAction.setEnabled(True)

            self.resize(self.automaticView.sizeHint() + QSize(80, 80 + self.menuBar().height()))

if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)

    window = MainWindow()
    if len(sys.argv) == 2:
        window.openFile(sys.argv[1])
    else:
        window.openFile('maps/mapexample.svg')
    window.show()
    sys.exit(app.exec_())
