import socket
import threading
import time
import re

from PySide.QtCore import *

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

        self.toSend = Queue()
        self.received = Queue()
        self.connected = False

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

            #Launching the socket's threads
            self.mainThread.start()
            self.receivingThread.start()

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
            self.received.put(received)
            print "Received : {}".format(received)

    def mainRoutine(self):
        print "[Socket] MAIN ROUTINE"
        while self.connected:

            # Sending what must be sent...
            query = self.toSend.get()
            self.socket.sendall(query)
            print "Sent : {}".format(query)

            while not self.received.empty():
                received = self.received.get()

                # Extracting the speed from the received
                avgSpeedSearch = re.search("avgSpeed : (-?\d+(?:[.]\d+)?)", received)
                if avgSpeedSearch:
                    self.car.setSpeed( 10*int(avgSpeedSearch.group(1)) )

                # print "Processing : {}".format(received)

        self.socket.sendall("DISCONNECT")
        self.socket.close()