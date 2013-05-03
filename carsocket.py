import socket
import threading
import time
import re

import sfml as sf
from PySide.QtCore import *

from math import copysign

from Queue import Queue
# from PySFML import sf

class CarSocket(QObject):
    speed = Signal(float)
    angle = Signal(float)
    temperature = Signal(float)
    position = Signal(QPointF)

    def __init__(self, car):
        super(CarSocket, self).__init__()

        self.car = car
        self.car.setSocket(self)

        self.socket = None

        self.mainThread = threading.Thread(target=self.mainRoutine)
        self.mainThread.daemon = True

        self.receivingThread = threading.Thread(target=self.receivingRoutine)
        self.receivingThread.daemon = True

        self.joystickThread = threading.Thread(target=self.joystickRoutine)
        self.joystickThread.daemon = True

        self.toSend = Queue()
        self.received = Queue()
        self.connected = False

        # Initialize Joystick
        sf.Joystick.update()

        self.running = False

        # # Connecting the signals
        # self.angle.connect(self.car.setAngle)
        # self.speed.connect(self.car.setSpeed)
        # self.temperature.connect(self.car.setTemperature)
        # self.speed.connect(self.car.setSpeed)


    def connect(self, ip, port):
        print "In connect socket"

        # Create a socket (SOCK_STREAM means a TCP socket)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            # Connect to server and send data
            self.socket.connect((ip, port))
            self.connected = True

            # Launching the socket's threads
            self.mainThread.start()
            self.receivingThread.start()

            # Launching the joystick's thread
            self.joystickThread.start()

        except Exception, e:
            print "Error when creating and connecting socket"
            print "Exception : {}".format(e)

    def formatCommand(self, operation, firstOperand = 0, secondOperand = 0):
        if operation > 99 or operation < - 9:
            raise Exception("Operation can't fit on two digits.")
        else:
            return "{0:02d}#{1:06d}#{2:06d}".format(operation, firstOperand, secondOperand)

    def send(self, query):
        if not self.connected:
            raise Exception("Car's socket is not connected. Can't send.")
        else:
            self.toSend.put(query)

    def receivingRoutine(self):
        print "[Socket] Receiving"
        while self.connected:
            received = self.socket.recv(1024)
            self.received.put(received)
            print "Received : {}".format(received)

    def joystickRoutine(self):
        """ Reads commands from the joystick and puts them in the sending queue """

        lastDir, x, y, lastRight, lastLeft = 0, 0, 0, 0, 0

        while self.connected:

            sf.Joystick.update()

            if sf.Joystick.is_connected(0):

                x = sf.Joystick.get_axis_position(0, sf.Joystick.X)
                y = sf.Joystick.get_axis_position(0, sf.Joystick.Y)

                # New style move :
                if x == 0 and y == 0:
                    direction, speedRight, speedLeft = 0, 0, 0
                else:
                    direction = int(copysign(1, -y))
                    percentRight = (100 + x) / 200.
                    percentLeft =  (100 - x) / 200.
                    
                    coef = 255. / max(percentRight, percentLeft)
                    
                    # Making sure the speed will always be >= 0 and <= 255
                    speedRight = max(0, min(255, int(coef * percentRight)))
                    speedLeft = max(0, min(255, int(coef * percentLeft)))


                if speedRight != lastRight or speedLeft != lastLeft or direction != lastDir:
                    self.toSend.put(self.formatCommand(direction, speedRight, speedLeft))

                    lastDir, lastRight, lastLeft = direction, speedRight, speedLeft

            time.sleep(0.005)

    def mainRoutine(self):
        print "[Socket] MAIN ROUTINE"
        while self.connected:

            # Sending what must be sent...
            query = self.toSend.get()
            self.socket.sendall(query)
            print "Sent : {}".format(query)

            # Processing what has been received
            while not self.received.empty():
                received = self.received.get()

                # Extracting the speed from the received
                avgSpeedSearch = re.search("avgSpeed : (-?\d+(?:[.]\d+)?)", received)
                if avgSpeedSearch:
                    self.car.setSpeed( 10*int(avgSpeedSearch.group(1)) )
                # print "Processing : {}".format(received)

            # A little sleep wouldn't do any harm and avoid 100% cpu :-)
            time.sleep(0.005)

        self.socket.sendall("DISCONNECT")
        self.socket.close()