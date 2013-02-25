# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'client_ui.ui'
#
# Created: Fri Feb  8 22:43:43 2013
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui
import socket
import threading
import time
import re
import pygame

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

# A "mediator" that transmits data from the network thread to the UI
class Logger(QtCore.QObject):
    logTrigger = QtCore.Signal(int)
    def __init__(self):
        super(Logger,self).__init__()
    def send(self, value):
        self.logTrigger.emit(value)


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(700, 415)
        Dialog.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.lcdNumber = QtGui.QLCDNumber(Dialog)
        self.lcdNumber.setEnabled(False)
        self.lcdNumber.setObjectName(_fromUtf8("lcdNumber"))
        self.verticalLayout.addWidget(self.lcdNumber)
        self.parametersBox = QtGui.QGroupBox(Dialog)
        self.parametersBox.setEnabled(False)
        self.parametersBox.setObjectName(_fromUtf8("parametersBox"))
        self.horizontalLayout_6 = QtGui.QHBoxLayout(self.parametersBox)
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem)
        self.groupBox_2 = QtGui.QGroupBox(self.parametersBox)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.horizontalLayout_5 = QtGui.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.pinNumber = QtGui.QSpinBox(self.groupBox_2)
        self.pinNumber.setObjectName(_fromUtf8("pinNumber"))
        self.horizontalLayout_5.addWidget(self.pinNumber)
        self.horizontalLayout_6.addWidget(self.groupBox_2)
        self.groupBox = QtGui.QGroupBox(self.parametersBox)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.groupBox)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.analogButton = QtGui.QRadioButton(self.groupBox)
        self.analogButton.setObjectName(_fromUtf8("analogButton"))
        self.horizontalLayout_4.addWidget(self.analogButton)
        self.digitalButton = QtGui.QRadioButton(self.groupBox)
        self.digitalButton.setObjectName(_fromUtf8("digitalButton"))
        self.horizontalLayout_4.addWidget(self.digitalButton)
        self.horizontalLayout_6.addWidget(self.groupBox)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem1)
        self.verticalLayout.addWidget(self.parametersBox)
        self.ConnectionBox = QtGui.QGroupBox(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ConnectionBox.sizePolicy().hasHeightForWidth())
        self.ConnectionBox.setSizePolicy(sizePolicy)
        self.ConnectionBox.setMaximumSize(QtCore.QSize(16777215, 75))
        self.ConnectionBox.setObjectName(_fromUtf8("ConnectionBox"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.ConnectionBox)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.ipInput = QtGui.QLineEdit(self.ConnectionBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ipInput.sizePolicy().hasHeightForWidth())
        self.ipInput.setSizePolicy(sizePolicy)
        self.ipInput.setMinimumSize(QtCore.QSize(250, 0))
        self.ipInput.setObjectName(_fromUtf8("ipInput"))
        self.horizontalLayout.addWidget(self.ipInput)
        self.portInput = QtGui.QLineEdit(self.ConnectionBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.portInput.sizePolicy().hasHeightForWidth())
        self.portInput.setSizePolicy(sizePolicy)
        self.portInput.setObjectName(_fromUtf8("portInput"))
        self.horizontalLayout.addWidget(self.portInput)
        self.connectButton = QtGui.QPushButton(self.ConnectionBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.connectButton.sizePolicy().hasHeightForWidth())
        self.connectButton.setSizePolicy(sizePolicy)
        self.connectButton.setMinimumSize(QtCore.QSize(150, 0))
        self.connectButton.setDefault(False)
        self.connectButton.setObjectName(_fromUtf8("connectButton"))
        self.horizontalLayout.addWidget(self.connectButton)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.verticalLayout.addWidget(self.ConnectionBox)
        self.closeGroup = QtGui.QGroupBox(Dialog)
        self.closeGroup.setMaximumSize(QtCore.QSize(16777215, 30))
        self.closeGroup.setTitle(_fromUtf8(""))
        self.closeGroup.setObjectName(_fromUtf8("closeGroup"))
        self.closeButton = QtGui.QPushButton(self.closeGroup)
        self.closeButton.setGeometry(QtCore.QRect(590, 0, 85, 30))
        self.closeButton.setMinimumSize(QtCore.QSize(0, 30))
        self.closeButton.setObjectName(_fromUtf8("pushButton"))
        self.verticalLayout.addWidget(self.closeGroup)

        #Connecting signals
        self.closeButton.clicked.connect(self.disconnectSocket)
        self.connectButton.clicked.connect(self.connectSocket)

        #Initializing the socket to None
        self.socket = None
        self.socketThread = None

        #Joystick
        # TODO : Make this a class instead of procedural functions
        pygame.init()
        pygame.joystick.init()
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        self.running = False
        self.turning = False

        #Initializing and connecting the logger
        self.logger = Logger()
        self.logger.logTrigger.connect(self.lcdNumber.display)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.parametersBox.setTitle(QtGui.QApplication.translate("Dialog", "Reading parameters", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("Dialog", "Pin\'s number", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Pin type", None, QtGui.QApplication.UnicodeUTF8))
        #radio button 1
        self.analogButton.setText(QtGui.QApplication.translate("Dialog", "Analog", None, QtGui.QApplication.UnicodeUTF8))
        self.digitalButton.setText(QtGui.QApplication.translate("Dialog", "Digital", None, QtGui.QApplication.UnicodeUTF8))
        self.ConnectionBox.setTitle(QtGui.QApplication.translate("Dialog", "Enter the server\'s IP and Port", None, QtGui.QApplication.UnicodeUTF8))
        self.ipInput.setText(QtGui.QApplication.translate("Dialog", "127.0.0.1", None, QtGui.QApplication.UnicodeUTF8))
        self.portInput.setText(QtGui.QApplication.translate("Dialog", "4242", None, QtGui.QApplication.UnicodeUTF8))
        self.connectButton.setText(QtGui.QApplication.translate("Dialog", "Connect", None, QtGui.QApplication.UnicodeUTF8))
        self.closeButton.setText(QtGui.QApplication.translate("Dialog", "Close", None, QtGui.QApplication.UnicodeUTF8))

    #METHODS

    def connectSocket(self):
        print "In connect socket"
        host = str(self.ipInput.text())
        port = int(self.portInput.text())
        # Create a socket (SOCK_STREAM means a TCP socket)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            # Connect to server and send data
            self.socket.connect((host, port))
            self.connected = True

            #Enabling reading UI
            self.lcdNumber.setEnabled(True)
            self.parametersBox.setEnabled(True)
            #Launching socket thread
            self.socketThread = threading.Thread(target=self.serverProcessing)
            self.socketThread.daemon = True
            self.socketThread.start()

        except:
            print "Error when creating and connecting socket"

    def disconnectSocket(self):
        print "In disconnectSocket"

        self.connected = False
	if self.socketThread:
        	self.socketThread.join()

        QtCore.QCoreApplication.instance().quit()

    def serverProcessing(self):
        print "begin sending"

        while self.connected:

            axisX = self.joystick.get_axis(1)
            axisY = self.joystick.get_axis(0)

            if axisX != 0 and not self.running:
                running = True

                if axisX > 0:
                    self.socket.sendall('-1')
                else:
                    self.socket.sendall('1')

            if axisY != 0 and not self.turning:
                turning = True

                if axisY > 0:
                    self.socket.sendall('2')
                else:
                    self.socket.sendall('-2')

            if (axisX == 0 and running) or (axisY == 0 and turning):
                self.socket.sendall('0')
                turning = False
                running = False

            pygame.event.pump()


        # while self.connected:
        #     print "reading iteration"
        #     pinNum = self.pinNumber.value()
        #     if self.analogButton.isChecked():
        #         type = "A"
        #     else:
        #         type = "D"
        #     self.socket.sendall("READ\r\n{}{}\r\n0".format(pinNum,type))

        #     # Receive data from the server
        #     received = self.socket.recv(1024)
        #     receivedMatch = re.match("OK\r\n([\d]+)", received)
        #     if receivedMatch:
        #         self.logger.send(int(receivedMatch.group(1)))
        #     else:
        #         print received

        #     time.sleep(0.3)

        self.socket.sendall("DISCONNECT")
        self.socket.close()


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
