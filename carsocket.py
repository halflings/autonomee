import socket
import threading
import time
import re

import sfml as sf
from PySide.QtCore import *

from math import copysign, radians

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

        self.toSend = Queue()
        self.received = Queue()
        self.connected = False

        # Initializing the Joystick
        sf.Joystick.update()
        self.running = False
        self.turning = False


        # Initializing the multiple threads (but not starting them)
        self.receivingThread = threading.Thread(target=self.receivingRoutine)
        self.receivingThread.daemon = True

        self.sendingThread = threading.Thread(target=self.sendingRoutine)
        self.sendingThread.daemon = True

        self.joystickThread = threading.Thread(target=self.joystickRoutine)
        self.joystickThread.daemon = True

        self.processingThread = threading.Thread(target=self.processingRoutine)
        self.processingThread.daemon = True

    def connect(self, ip, port):
        print "In connect socket"

        # Create a socket (SOCK_STREAM means a TCP socket)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            # Connect to server and send data
            self.socket.connect((ip, port))
            self.connected = True

            # Launching the socket's threads
            self.receivingThread.start()
            self.sendingThread.start()

            self.processingThread.start()

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

    def sendingRoutine(self):
        print "[Socket] SENDING ROUTINE"

        while self.connected:
            query = self.toSend.get()
            self.socket.sendall(query)
            print "Sent : {}".format(query)

    def receivingRoutine(self):
        print "[Socket] RECEIVING ROUTINE"

        while self.connected:
            received = self.socket.recv(1024)
            
            if len(received) == 0:
                self.connected = False
            else:
                self.received.put(received)
                print "Received : {}".format(received)

    def joystickRoutine(self):
        """ Reads commands from the joystick and puts them in the sending queue """

        print "[Socket] JOYSTICK ROUTINE"

        lastDir, x, y, lastRight, lastLeft = 0, 0, 0, 0, 0

        while self.connected:

            sf.Joystick.update()

            if sf.Joystick.is_connected(0):

                x = sf.Joystick.get_axis_position(0, sf.Joystick.X)
                y = sf.Joystick.get_axis_position(0, sf.Joystick.Y)

                # Old style move
                if (self.running or self.turning) and x == 0 and y == 0:
                    self.running = False
                    self.turning = False
                    self.send(formatCommand(STOP))

                elif not self.running and y != 0:
                    self.running = True
                    
                    if y < 0:
                        self.send(formatCommand(RUN_FORWARD))
                    else:
                        self.send(formatCommand(RUN_BACKWARD))

                elif not self.turning and x != 0:
                    self.turning = True
                    
                    if x > 0:
                        self.send(formatCommand(TURN_RIGHT))
                    else:
                        self.send(formatCommand(TURN_LEFT))


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
                #     self.send(formatCommand(direction, speedRight, speedLeft))

                #     lastDir, lastRight, lastLeft = direction, speedRight, speedLeft

                time.sleep(0.005)

    def processingRoutine(self):
        print "[Socket] PROCESSING ROUTINE"
        while self.connected:

            # Processing what has been received
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
                angle = radians(float(angleSearch.group(1))) 
                self.car.setAngle(angle)

            # Extracting the closest distance
            distanceSearch = re.search("Distance : (-?\d+(?:[.]\d+)?)", received)
            if distanceSearch:
                print "Got distance : {}".format(distanceSearch.group(1))
                self.car.distance = float(distanceSearch.group(1))
                self.car.notify()

        self.socket.sendall("DISCONNECT")
        self.socket.close()

    def setServo(self, angle):
        # Making sure : -80 <= angle <= 80
        angle = max(-80, min(80, angle))
        self.send(formatCommand(TURN_SERVO, angle))