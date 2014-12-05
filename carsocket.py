import socket
import threading
import re

import sfml as sf
from PySide.QtCore import *

from math import radians
from engine import Car
from Queue import Queue
from time import sleep

TURN_LEFT, RUN_BACKWARD, STOP, RUN_FORWARD, TURN_RIGHT, SWEEP_SERVO, TURN_SERVO, SET_SPEED = range(-2, 6)

def formatCommand(operation, firstOperand = 0, secondOperand = 0):
    if operation > 99 or operation < - 9:
        raise Exception("Operation can't fit on two digits.")
    else:
        return "{0:02d}#{1:06d}#{2:06d}".format(operation, firstOperand, secondOperand)

class CarSocket(QObject):

    logSignal = Signal(str, str)

    def __init__(self, car):
        super(CarSocket, self).__init__()

        self.car = car
        self.car.setSocket(self)

        # Create a socket (SOCK_STREAM means a TCP socket)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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
        self.logSignal.emit(text, mode)
        print "[CarSocket] {}".format(text)

    def connect(self, ip, port):
        self.log("Attempting connection to {}:{}".format(ip, port))

        try:
            # Connect to server and send data
            self.socket.settimeout(0.100)
            self.socket.connect((ip, port))
            self.socket.settimeout(None)

            self.connected = True

            # Launching the socket's threads
            self.receivingThread.start()
            self.sendingThread.start()

            self.processingThread.start()

            # Launching the joystick's thread
            self.joystickThread.start()

            return True

        except Exception, e:
            self.log("Error when creating and connecting socket", mode='ERROR')
            self.log("Exception : {}".format(e), mode='ERROR')

            return False

    def send(self, query):
        if not self.connected:
            raise Exception("Car's socket is not connected. Can't send.")
        else:
            self.toSend.put(query)

    def sendingRoutine(self):
        self.log("SENDING ROUTINE")

        while self.connected:
            query = self.toSend.get()
            self.socket.sendall(query)
            print "Sent : {}".format(query)

    def receivingRoutine(self):
        self.log("RECEIVING ROUTINE")

        while self.connected:
            try:
                received = self.socket.recv(1024)
                if len(received) == 0:
                    self.connected = False
                else:
                    self.received.put(received)
                    #self.log("Received : {}".format(received))
                sleep(0.005)
            except socket.error, e:
                self.log("Couldn't receive from server [Exception : {}]. Disconnecting.".format(e))
                self.connected = False

    def joystickRoutine(self):
        """ Reads commands from the joystick and puts them in the sending queue """

        self.log("JOYSTICK ROUTINE")

        while self.connected:
            sleep(0.005)
            sf.Joystick.update()

            if sf.Joystick.is_connected(0):

                x = sf.Joystick.get_axis_position(0, sf.Joystick.X)
                y = sf.Joystick.get_axis_position(0, sf.Joystick.Y)

                command = None

                # Old style move
                if (self.running or self.turning) and x == 0 and y == 0:
                    command = STOP

                    self.running = False
                    self.turning = False
                elif x != 0 or y != 0:
                    if abs(x) > abs(y) and not self.turning:
                        command  = TURN_RIGHT if x > 0 else TURN_LEFT

                        self.turning = True
                        self.running = False

                    elif abs(y) > abs(x) and not self.running:
                        command = RUN_FORWARD if y < 0 else RUN_BACKWARD

                        self.running = True
                        self.turning = False

                if command is not None:
                    self.send(formatCommand(command))

    def processingRoutine(self):
        self.log("PROCESSING ROUTINE")
        while self.connected:

            # Processing what has been received
            received = self.received.get()
            floatPattern = "-?\d+(?:[.]\d+)?"

            if self.car.mode == Car.Manual:
                # Extracting the speed from the received
                speedSearch = re.search("Speed : ({})".format(floatPattern), received)
                if speedSearch:
                    #self.log("Got speed : {}".format(speedSearch.group(1)))
                    self.car.setSpeed( 3*float(speedSearch.group(1)) )

                # Extracting the angle
                angleSearch = re.search("Angle : ({})".format(floatPattern), received)
                if angleSearch:
                    #self.log("Got angle : {}".format(angleSearch.group(1)))
                    angle = radians(float(angleSearch.group(1))) 
                    self.car.setAngle(angle)

                # Extracting the closest distance
                distanceSearch = re.search("Distance : ({})".format(floatPattern), received)
                if distanceSearch:
                    #self.log("Got distance : {}".format(distanceSearch.group(1)))
                    # The received distance is in cm, we convert it to mm
                    self.car.distance = float(distanceSearch.group(1))*10
                    self.car.notify()

                temperatureSearch = re.search("Temperature : ({})".format(floatPattern), received)
                if temperatureSearch:
                    #self.log("Got temperature : {}".format(temperatureSearch.group(1)))
                    self.car.temperature = float(temperatureSearch.group(1))
                    self.car.notify()

                # Extracting the car's position
                positionSearch = re.search("Position : [(](\d+), (\d+)[)]", received)
                if positionSearch:
                    x, y = int(positionSearch.group(1)), int(positionSearch.group(2))
                    #self.log("Got position : ({}, {})".format(x, y))

                    #xOff, yOff = self.car.map.width/2, self.car.map.height/2
                    #self.car.x, self.car.y = x + xOff, y + yOff
                    #self.car.notify()
            sleep(0.0005)

        self.socket.sendall("DISCONNECT")
        self.socket.close()

    def setServo(self, angle):
        # Making sure : -80 <= angle <= 80
        angle = max(-80, min(80, angle))
        self.send(formatCommand(TURN_SERVO, angle))

    def setMaxSpeed(self, maxspeed):
        self.send(formatCommand(SET_SPEED, maxspeed))
