#!/usr/bin/env python

"""
server.py - communicates with the Arduino (throught serial communication) and
sends data back to a remote clients.
Meant to run on a RaspberryPi.
"""

import SocketServer
import socket
import serial
import threading
import sys
from Queue import Queue
from time import sleep

NOARDUINO = 'noarduino' in sys.argv
if NOARDUINO:
    print "NoArduino mode activated"

USB_PATH = '/dev/ttyACM0'
DEFAULT_IP = '10.0.0.42'

def getAddress():
    try:
        address = socket.gethostbyname(socket.gethostname())
        # This often give 127.0.0.1, so ...
    except:
        address = ''
    if not address or address.startswith('127.'):
        # ...the hard way.
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((DEFAULT_IP, 0))
        address = s.getsockname()[0]
    return address

class PiHandler(SocketServer.BaseRequestHandler, object):


    def setup(self):
        super(PiHandler, self).setup()
        self.connected = True
	if NOARDUINO:
            self.arduino = None
        else:
            self.arduino = serial.Serial(USB_PATH, 9600)

        self.queries = Queue()
        self.receiveThread = threading.Thread(target = self.receptionRoutine)
        self.receiveThread.daemon = True
	self.receiveThread.start()

    def send(self, data):
        self.request.sendall(data)
        print "Sent '{}'".format(data)

    def receptionRoutine(self):
        while self.connected:
            data = self.request.recv(1024)
            print "Client sent '{}'".format(data)
            if len(data) == 0:
                print "Got an empty message"
                self.connected = False

            self.queries.put(data)
	    sleep(0.005)

    def serialReadRoutine(self):
        while self.connected:
	    while self.arduino.inWaiting() > 0:
		try:
                    line = self.arduino.readline()
		    #print "Car wrote : '{}'".format(line)
		    # We send what the car wrote back to the client
		    self.send(line)
                except:
                    print "Couldn't write on the arduino. Disconnecting"
                    self.connected = False
        sleep(0.005)

    def handle(self):
        print "New connection"
        loopNumber = 0

	if self.arduino is not None:
	    serialReadThread = threading.Thread(target=self.serialReadRoutine)
	    serialReadThread.daemon = True
	    serialReadThread.start()

        while self.connected:
            loopNumber += 1
            print "Connected loop #{}".format(loopNumber)
            print "-"*30

            #We write the value we receive to the Arduino
            query = self.queries.get()

            if self.arduino is not None:
                self.arduino.write(query)

            if query == 'DISCONNECT' or len(query) == 0:
                self.connected = False
            sleep(0.005)

	print "Disconnecting"

	if self.arduino is not None:
            self.arduino.write('0')
            self.arduino.close()

class PiServer(SocketServer.TCPServer):
    """
    A TCP server, running on the Raspberry Pi, that controls the Arduino
    by sending serial messages
    """
    allow_reuse_address = True
    def __init___(self, address, handler):
        super(PiServer,self).__init__(address, handler)


if __name__ == "__main__":

    host = getAddress()
    port = 4242
    print "Server connected on {}:{}".format(host, port)
    server = PiServer((host, port), PiHandler)
    server.serve_forever()
