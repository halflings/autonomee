import SocketServer
import socket
import serial

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

	def send(self, data):
		self.request.sendall(data)
		print "Sent '{}'".format(data)


	def handle(self):
    		# Serial connection with the Arduno, at 9600 bauds
    		# NOTE : this should be on the server, but that causes bugs
		self.arduino = serial.Serial(USB_PATH, 9600)

		print "New connection"
		connected = True
		while connected:
			print "In connected iteration"
			self.data = self.request.recv(1024)
			print "Received : [{}]".format(self.data)
			self.arduino.write(self.data)
			if self.data == '3':
				sensorData = self.arduino.readline()
				print "Sensor data = {}".format(sensorData)
				self.request.sendall(sensorData)
	        	print '-'*15

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

	server = PiServer((host, port), PiHandler)
	server.serve_forever()
