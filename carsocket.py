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

    logger = Signal(str, str)

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

    def log(self, text, mode='DEBUG'):
        self.logger.emit(text, mode)

    def connect(self, ip, port):
        self.log("Connecting the socket")

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
            self.log("Error when creating and connecting socket", mode='ERROR')
            self.log("Exception : {}".format(e), mode='ERROR')

    def send(self, query):
        if not self.connected:
            raise Exception("Car's socket is not connected. Can't send.")
        else:
            self.toSend.put(query)

    def sendingRoutine(self):
        self.log("[Socket] SENDING ROUTINE")

        while self.connected:
            query = self.toSend.get()
            self.socket.sendall(query)
            print "Sent : {}".format(query)

    def receivingRoutine(self):
        self.log("[Socket] RECEIVING ROUTINE")

        while self.connected:
            received = self.socket.recv(1024)
            
            if len(received) == 0:
                self.connected = False
            else:
                self.received.put(received)
                print "Received : {}".format(received)

    def joystickRoutine(self):
        """ Reads commands from the joystick and puts them in the sending queue """

        self.log("[Socket] JOYSTICK ROUTINE")

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
        self.log("[Socket] PROCESSING ROUTINE")
        while self.connected:

            # Processing what has been received
            received = self.received.get()

            floatPattern = "-?\d+(?:[.]\d+)?"

            # Extracting the speed from the received
            speedSearch = re.search("Speed : ({})".format(floatPattern), received)
            if speedSearch:
                self.log("Got speed : {}".format(speedSearch.group(1)))
                self.car.setSpeed( 10*float(speedSearch.group(1)) )

            # Extracting the angle
            angleSearch = re.search("Angle : ({})".format(floatPattern), received)
            if angleSearch:
                self.log("Got angle : {}".format(angleSearch.group(1)))
                angle = radians(float(angleSearch.group(1))) 
                self.car.setAngle(angle)

            # Extracting the closest distance
            distanceSearch = re.search("Distance : ({})".format(floatPattern), received)
            if distanceSearch:
                self.log("Got distance : {}".format(distanceSearch.group(1)))
                self.car.distance = float(distanceSearch.group(1))
                self.car.notify()

            # Extracting the car's position
            positionSearch = re.search("Position : [(](\d+), (\d+)[)]", received)
            if positionSearch:
                x, y = int(positionSearch.group(1)), int(positionSearch.group(2))
                self.log("Got position : ({}, {})".format(x, y))
                
                xOff, yOff = self.car.map.width/2, self.car.map.height/2
                self.car.x, self.car.y = x + xOff, y + yOff
                self.car.notify()

        self.socket.sendall("DISCONNECT")
        self.socket.close()

    def setServo(self, angle):
        # Making sure : -80 <= angle <= 80
        angle = max(-80, min(80, angle))
        self.send(formatCommand(TURN_SERVO, angle))