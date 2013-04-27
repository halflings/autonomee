#!/usr/bin/env python

"""
    main.py - application entry point and the main window (opening files, menus, ...).
"""

from PySide import QtCore, QtGui
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtUiTools import *

from manual import ManualView
from auto import AutoView
import engine
import configdialog


class MainWindow(QMainWindow):
    AUTO_MODE = 0
    MANUAL_MODE = 1

    def __init__(self):
        super(MainWindow, self).__init__()

        self.currentPath = ''

        # The car's model, shared between the different views
        self.car = engine.Car()

        # Setting the views
        self.automaticView = AutoView(self.car)
        self.manualView = ManualView(self.car)

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

        # Mode switching (automatic-manual) menu
        modeMenu = QMenu("&Mode", self)

        manualAction = modeMenu.addAction("M&anual")
        manualAction.setShortcut("Ctrl+M")
        manualAction.triggered.connect(self.manualMode)

        automaticAction = modeMenu.addAction("A&utomatic")
        automaticAction.setShortcut("Ctrl+A")
        automaticAction.triggered.connect(self.automaticMode)

        self.menuBar().addMenu(modeMenu)

        # Stacked widget (containing the auto. and manual view)
        self.stackedWidget = QStackedWidget()
        self.stackedWidget.addWidget(self.automaticView)
        self.stackedWidget.addWidget(self.manualView)

        self.setCentralWidget(self.stackedWidget)
        self.setMinimumSize(800, 600)

        # Configuration button
        self.configButton = QPushButton("Configuration panel", parent=self.automaticView)
        self.configButton.clicked.connect(self.openConfigPanel)

        # Configuration dialog
        loader = QUiLoader()
        file = QtCore.QFile("config.ui")
        file.open(QtCore.QFile.ReadOnly)
        self.config = loader.load(file)
        file.close()

        self.config.connectButton.clicked.connect(self.connectCar)
        self.config.buttonBox.accepted.connect(self.acceptConfig)
        self.config.buttonBox.rejected.connect(self.config.reject)
        self.config.buttonBox.button(QDialogButtonBox.RestoreDefaults).clicked.connect(self.resetConfig)

    def manualMode(self):
        self.stackedWidget.setCurrentWidget(self.manualView)
        self.setWindowTitle("Carosif - Manual mode")

    def automaticMode(self):
        self.stackedWidget.setCurrentWidget(self.automaticView)
        self.setWindowTitle("Carosif - Automatic mode - Map : {}".format(self.currentPath))

    def connectCar(self):
        ip = self.config.ipEdit.toPlainText()
        port = int(self.config.portEdit.toPlainText())

        print "Connecting robot to {}:{}".format(ip, port)

    def openConfigPanel(self):
        self.config.show()

    def acceptConfig(self):
        try:
            c = self.config
            self.car.width = int(c.widthValue.toPlainText())
            self.car.length = int(c.lengthValue.toPlainText())

            self.car.sensor_noise = float(c.sensorValue.text())
            self.car.displacement_noise = float(c.displacementValue.text())
            self.car.rotation_noise = float(c.rotationValue.text())

            self.car.update()

            self.config.accept()
        except:
            print "Parsing error"
            # TODO : Do this in the status bar, not in the console

    def resetConfig(self):
        c = self.config
        c.widthValue.setPlainText(str(engine.Car.def_width))
        c.lengthValue.setPlainText(str(engine.Car.def_length))

        c.sensorSlider.setValue(int(engine.Car.def_sensor))
        c.rotationSlider.setValue(int(engine.Car.def_rotation))
        c.displacementSlider.setValue(int(engine.Car.def_displacement))

    def resizeEvent(self, event):
        x, y = self.size().width(), self.size().height()
        self.configButton.setGeometry(QRect(x-230, y-80, 200, 40))

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
    QTextCodec.setCodecForCStrings(QTextCodec.codecForName("UTF-8"))
    QTextCodec.setCodecForTr(QTextCodec.codecForName("UTF-8"))

    window = MainWindow()
    if len(sys.argv) == 2:
        window.openFile(sys.argv[1])
    else:
        window.openFile('maps/mapexample.svg')
    window.show()
    sys.exit(app.exec_())
