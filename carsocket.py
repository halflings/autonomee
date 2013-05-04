import socket
import threading
import time
import re

import sfml as sf
from PySide.QtCore import *

from math import copysign

from Queue import Queue
# from PySFML import sf

TURN_LEFT, RUN_BACKWARD, STOP, RUN_FORWARD, TURN_RIGHT, SWEEP_SERVO, TURN_SERVO = range(-2, 5)

def formatCommand(operation, firstOperand = 0, secondOperand = 0):
    if operation > 99 or operation < - 9:
        raise Exception("Operation can't fit on two digits.")
    else:
        return "{0:02d}#{1:06d}#{2:06d}".format(operation, firstOperand, secondOperand)


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
        self.turning = False

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

    def send(self, query):
        if not self.connected:
            raise Exception("Car's socket is not connected. Can't send.")
        else:
            self.toSend.put(query)

    def receivingRoutine(self):
        print "[Socket] Receiving"
        while self.connected:
            received = self.socket.recv(1024)
            
            if len(received) == 0:
                self.connected = False
            else:
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

                # Old style move
                if (self.running or self.running) and x == 0 and y == 0:
                    self.running = False
                    self.turning = False
                    self.toSend.put(formatCommand(STOP))

                elif not self.running and y != 0:
                    self.running = True
                    
                    if y < 0:
                        self.toSend.put(formatCommand(RUN_FORWARD))
                    else:
                        self.toSend.put(formatCommand(RUN_BACKWARD))

                elif not self.turning and x != 0:
                    self.turning = True
                    
                    if x > 0:
                        self.toSend.put(formatCommand(TURN_RIGHT))
                    else:
                        self.toSend.put(formatCommand(TURN_LEFT))


                # New style move (percent on right/left wheel)
                # if x == 0 and y == 0:
                #     direction, speedRight, speedLeft = 0, 0, 0
                # else:
                #     direction = int(copysign(1, -y))
                #     percentRight = (100 + x) / 200.
                #     percentLeft =  (100 - x) / 200.
                    
                #     coef = 250. / max(percentRight, percentLeft)
                    
                #     # Making sure the speed will always be >= 0 and <= 255
                #     speedRight = max(0, min(250, int(coef * percentRight)))
                #     speedLeft = max(0, min(250, int(coef * percentLeft)))

                # if speedRight != lastRight or speedLeft != lastLeft or direction != lastDir:
                #     self.toSend.put(formatCommand(direction, speedRight, speedLeft))

                #     lastDir, lastRight, lastLeft = direction, speedRight, speedLeft

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

                floatPattern = "(-?\d+(?:[.]\d+)?)"

                # Extracting the speed from the received
                avgSpeedSearch = re.search("avgSpeed : {}".format(floatPattern), received)
                if avgSpeedSearch:
                    print "Got speed : {}".format(speedSearch.group(1))
                    self.car.setSpeed( 10*float(avgSpeedSearch.group(1)) )

                # Extracting the angle
                angleSearch = re.search("Angle : (-?\d+(?:[.]\d+)?)", received)
                if angleSearch:
                    print "Got angle : {}".format(angleSearch.group(1))
                    self.car.seAngle( float(angleSearch.group(1)) )

                # Extracting the closest distance
                distanceSearch = re.search("Distance : (-?\d+(?:[.]\d+)?)", received)
                if distanceSearch:
                    print "Got distance : {}".format(distanceSearch.group(1))
                    self.car.distance = float(distanceSearch.group(1))

                # print "Processing : {}".format(received)

            # A little sleep wouldn't do any harm and avoid 100% cpu :-)
            time.sleep(0.005)

        self.socket.sendall("DISCONNECT")
        self.socket.close()

    def setServo(self, angle):
        # Making sure : -80 <= angle <= 80
        angle = max(-80, min(80, angle))
        self.toSend.put(formatCommand(TURN_SERVO, angle))