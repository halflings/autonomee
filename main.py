#!/usr/bin/env python

"""
    main.py - application entry point and the main window (opening files, menus, ...).
"""

from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtUiTools import *

from manual import ManualView
from auto import AutoView
from svg import SvgTree
from carsocket import CarSocket
from probability import ParticleFilter
from widgets import NotificationTooltip

import engine
import datetime
import time

class MainWindow(QMainWindow):
    AUTO_MODE = 0
    MANUAL_MODE = 1

    def __init__(self):
        super(MainWindow, self).__init__()

        self.currentPath = ''

        # The car's model, shared between the different views
        self.car = engine.Car()

        # Socket (to connect with the car/Rpi)
        self.carSocket = CarSocket(self.car)

        # Setting the views
        self.automaticView = AutoView(self.car)
        self.manualView = ManualView(self.car)

        # File menu
        fileMenu = QMenu("&File", self)
        openAction = fileMenu.addAction("&Open...")
        openAction.setShortcut("Ctrl+O")

        saveAction = fileMenu.addAction("&Save...")
        saveAction.setShortcut("Ctrl+S")
        
        setScale = fileMenu.addAction("Set map's scale")
        setAngle = fileMenu.addAction("Set map's orientation")

        quitAction = fileMenu.addAction("E&xit")
        quitAction.setShortcut("Ctrl+Q")

        openAction.triggered.connect(self.openFile)
        saveAction.triggered.connect(self.saveMap)
        setScale.triggered.connect(self.setScale)
        setAngle.triggered.connect(self.setAngle)
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

        # Configuration dialog
        loader = QUiLoader()
        file = QFile("config.ui")
        file.open(QFile.ReadOnly)
        self.config = loader.load(file)
        file.close()

        self.config.connectButton.clicked.connect(self.connectCar)
        self.config.buttonBox.accepted.connect(self.acceptConfig)
        self.config.buttonBox.rejected.connect(self.config.reject)
        self.config.buttonBox.button(QDialogButtonBox.RestoreDefaults).clicked.connect(self.resetConfig)
        self.config.resetParticles.clicked.connect(self.resetParticles)

        # Log dialog
        file = QFile("log.ui")
        file.open(QFile.ReadOnly)
        self.log = loader.load(file)
        file.close()

        self.log.saveButton.clicked.connect(self.saveLog)

        # self.carSocket.logSignal.connect(self.addToLog)

        self.initLog()

        # Configuration button
        self.configButton = QPushButton("Configuration panel", parent=self.automaticView)
        self.configButton.clicked.connect(self.openConfigPanel)

        # Configuration button
        self.logButton = QPushButton("Car's log", parent=self.automaticView)
        self.logButton.clicked.connect(self.log.show)
        # self.logButton.setVisible(False)


    def manualMode(self):
        self.stackedWidget.setCurrentWidget(self.manualView)
        self.setWindowTitle("Autonomee - Manual mode")

    def automaticMode(self):
        self.stackedWidget.setCurrentWidget(self.automaticView)
        self.setWindowTitle("Autonomee - Automatic mode - Map : {}".format(self.currentPath))

    def saveMap(self):
        self.automaticView.scene().map.save()

    def setAngle(self):
        self.automaticView.scene().setMapNorthAngle()
        self.car.updateMap()

    def setScale(self):
        self.automaticView.scene().setMapScale()
        self.car.updateMap()

    def saveLog(self):
        with open("log.html", 'w+') as logFile:
            logFile.write(self.log.logEdit.toHtml())
            logFile.close()

    def initLog(self):
        curDate = datetime.date.today().strftime("%A %d. %B %Y")
        curTime = time.strftime('%H:%M:%S', time.localtime())
        self.addToLog("<h3>Date : {} | Time: {}</h3>".format(curDate, curTime))

    def addToLog(self, text, mode='NORMAL'):
        if mode == 'RAW':
            toAdd = text
        else:
            toAdd = "<p>{}</p> \n <hr> \n".format(text)
        self.log.logEdit.append(toAdd)

    def openConfigPanel(self):
        # Updating dialog with the configuration 
        
        c = self.config
        c.widthValue.setPlainText(str(self.car.width))
        c.lengthValue.setPlainText(str(self.car.length))

        c.sensorSlider.setValue(int(self.car.sensor_noise))
        c.rotationSlider.setValue(int(self.car.rotation_noise))
        c.displacementSlider.setValue(int(self.car.displacement_noise))

        self.config.show()

    def resetParticles(self):
        self.automaticView.scene().particleFilter.reset()
        self.automaticView.scene().heatmap.update()

    def notify(self, text, type):
        """ Creates a notification tooltip in the 'automatic' view """
        self.automaticView.scene().notify(text, type)

    def connectCar(self):
        """ Connecting the app to the car """
        ip = self.config.ipEdit.toPlainText()
        port = int(self.config.portEdit.toPlainText())

        print "Connecting robot to {}:{}".format(ip, port)

        connected = self.carSocket.connect(ip, port)

        if connected:
            self.notify("Succesfully connected to the car !", type=NotificationTooltip.information)
            self.config.reject()
        else:
            self.notify("Couldn't connect to the car.", type=NotificationTooltip.error)

    def acceptConfig(self):
        """ Validating the parameters from the configuration dialog """
        try:
            c = self.config
            self.car.width = int(c.widthValue.toPlainText())
            self.car.length = int(c.lengthValue.toPlainText())

            self.car.sensor_noise = float(c.sensorValue.text())
            self.car.displacement_noise = float(c.displacementValue.text())
            self.car.rotation_noise = float(c.rotationValue.text())

            if c.simpleProba.isChecked():
                self.automaticView.scene().particleFilter.mode = ParticleFilter.simple
            elif c.markovProba.isChecked():
                self.automaticView.scene().particleFilter.mode = ParticleFilter.markov

            self.car.update()

            self.car.updateMap()

            self.config.accept()

            self.notify("The application's configuration was updated", type=NotificationTooltip.information)


        except ValueError:
            self.notify("Couldn't parse the given values !", type=NotificationTooltip.error)

            self.config.reject()
            # TODO : Do this in the status bar, not in the console

    def resetConfig(self):
        """ Reseting the parameters from the configuration dialog """
        c = self.config
        c.widthValue.setPlainText(str(engine.Car.def_width))
        c.lengthValue.setPlainText(str(engine.Car.def_length))

        c.sensorSlider.setValue(int(engine.Car.def_sensor))
        c.rotationSlider.setValue(int(engine.Car.def_rotation))
        c.displacementSlider.setValue(int(engine.Car.def_displacement))

        self.notify("All parameters were reset to their default value", type=NotificationTooltip.information)


    def resizeEvent(self, event):
        h = 40
        cW, lW = 200, 150

        x, y = self.size().width(), self.size().height()
        
        y -= h + 35
        x -= cW + 15
        self.configButton.setGeometry(QRect(x, y, cW, h))
        
        x -= lW + 15
        self.logButton.setGeometry(QRect(x, y, lW, h))

    def openFile(self, path=None):
        if not path:
            path = QFileDialog.getOpenFileName(self, "Open SVG File", self.currentPath, "SVG files (*.svg *.svgz *.svg.gz)")[0]
        if path:
            svgFile = QFile(path)
            if not svgFile.exists():
                QMessageBox.critical(self, "Open SVG File", "Could not open file '%s'." % path)
                self.backgroundAction.setEnabled(True)
                return

            self.svgMap = SvgTree(svgFile.fileName(), radius=max(self.car.width, self.car.length))
            self.automaticView.openMap(self.svgMap)

            if not path.startswith(':/'):
                self.currentPath = path
                self.setWindowTitle("Autonomee - Automatic mode - Map : {}".format(self.currentPath))
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
