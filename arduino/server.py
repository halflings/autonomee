import SocketServer
import socket
import serial
import re
import threading
from Queue import Queue
from time import sleep


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
            print "Received '{}'".format(data)
            self.queries.put(data)

        # Serial connection with the Arduno, at 9600 bauds
        # NOTE : this should be on the server, but that causes bugs


	def handle(self):
		print "New connection with : {}\n".format(self.request.address)
        loopNumber = 0
        while self.connected:
            loopNumber += 1
            print "Connected loop #{}".format(loopNumber)
            print "-"*30

            #We write the value we receive to the Arduino
            query = self.queries.get()
            self.arduino.write(query)

            #If the remote client is requesting angular distances
            if int(query) == 3:
                #We read the angular distances sent by the Arduino
                sensorData = dict()
                while self.arduino.inWaiting() > 0:
                    angle = int(self.arduino.readline())
                    distance = int(self.arduino.readline())
                    sensorData[angle] = distance
                    print "Read sensor data : dist {} at angle {}".format(distance, angle)
                    sleep(0.03)

            #We send the number of measurements to the client
            self.send(str(len(sensorData)))

            #... then we send the measurements one after another
            for angle in sensorData:
                self.send("A{}\r\nD{}\r\n".format(angle, sensorData[angle]))

        self.arduino.write('0')
        self.arduino.close()

			# print "In connected iteration"
			# self.data = self.request.recv(1024)
			# print "Received : [{}]".format(self.data)
			# self.arduino.write(self.data)
			# if self.data == '3':
			# 	sensorData = []
			# 	while self.arduino.inWaiting() > 0:
			# 		angle = int(self.arduino.readline())
			# 		distance = int(self.arduino.readline())
			# 		sensorData[angle] = distance
			# 		print "Sensor at angle {} : {}".format(angle, distance)

			# 	# We first send the number of measurements
   #              self.request.send(str(len(sensorData)))
			# 	# We send one by one the sensor measurements
   #              for angle in sensorData:
   #                  self.send("A{}\r\nD{}\r\n".format(angle, sensorData[angle]))

   #              print '-'*15


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

	server = PiServer((host, port), PiHandler)
	server.serve_forever()
