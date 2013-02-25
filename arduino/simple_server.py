import SocketServer
import socket
import serial

USB_PATH = '/dev/bus/usb/001/003'

def getAddress():
    try:
        address = socket.gethostbyname(socket.gethostname())
        # This often give 127.0.0.1, so ...
    except:
        address = ''
    if not address or address.startswith('127.'):
        # ...the hard way.
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('4.2.2.1', 0))
        address = s.getsockname()[0]
    return address

class PiHandler(SocketServer.BaseRequestHandler, object):

	def send(self, data):
		self.request.sendall(data)
		print "Sent '{}'".format(data)

	def handle(self):
		print "New connection"
		connected = True
		while connected:
			print "In connected iteration"
			self.data = self.request.recv(1024)
			print "Received : [{}]".format(self.data)
			self.ardino.write(self.data)
	        print "Wrote input on the arduino"
	        print '-'*15

#TCPServer that should run on the Raspberry Pi
class PiServer(SocketServer.TCPServer):
    allow_reuse_address = True

    def __init___(self, address, handler):
    	super(PiServer,self).__init__(address, handler)
    	# Serial connection with the Arduino, at 9600 bauds
    	self.arduino = serial.Serial(USB_PATH, 9600)


if __name__ == "__main__":

	host = getAddress()
	port = 4242

	server = PiServer((host, port), PiHandler)
	server.serve_forever()
