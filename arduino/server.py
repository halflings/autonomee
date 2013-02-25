import SocketServer
import re
from arduino import Arduino

class PiHandler(SocketServer.BaseRequestHandler, object):
	read_pattern="READ\r\n([\d]+)(A|D)"
	write_pattern="WRITE\r\n([\d]+)(A|D)\r\n([\d]+)"

	def send(self, data):
		self.request.sendall(data)
		print "Sent '{}'".format(data)

	def handle(self):
		print "New connection"

		connected = True
		while connected:
			print "In connected iteration"
			self.data = self.request.recv(1024)
			print "Got {}".format(self.data)
			readMatch = re.search(PiHandler.read_pattern, self.data)
			writeMatch = re.search(PiHandler.write_pattern, self.data)

			value = None
			if readMatch:
				print "HOORAY READMATCH"

			if self.data == "DISCONNECT	":
				print "In disconnect"
				connected = False
			elif writeMatch:
				print "In writeMatch"
				# pin = int(writeMatch.group(<1))
				# type = writeMatch.group(2)
				# value = int(writeMatch.group(2))
				# if type=="A":
				# 	self.arduino.analogWrite(pin, value)
				# 	self.send("OK\r\n{}".format(value)
				# elif value==0:
				# 	self.arduino.digitalWrite(pin, "LOW")
				# 	self.send("OK\r\n{}".format(value)
				# elif value==0:
				# 	self.arduino.digitalWrite(pin, "HIGH")
				# 	self.send("OK\r\n{}".format(value))
				# else:
				# 	self.send("ERROR : Digital value must be 0 or 1")
			elif readMatch:
				print "In readMATCH"
				print "In readMatch"
				pin = int(readMatch.group(1))
				type = readMatch.group(2)
				print "Asked for {} pin #{}".format(type, pin)

				value = pin/2
				# just send half the pin's number
		        print "Pin in range, sending : {}".format("OK\r\n{}".format(value))
		        self.request.sendall("OK\r\n{}".format(value))

		        # if type=="A" and num in range(45):
		        # 	value = self.arduino.analogRead(num)
		        # elif type=="D" and num in range(30):
		        # 	value = self.arduino.digitalRead(num)
		        # else:
		        # 	print "Pin out of range"
		        # 	self.request.sendall("ERR : Pin number out of range\r\n")

        	else:
        		print "Can't interpret query"
	        	self.request.sendall("ERROR : Can't interpret query")

	        print "End of iteration"


#TCPServer that should run on the Raspberry Pi
class PiServer(SocketServer.TCPServer):
    allow_reuse_address = True

    def __init___(self, address, handler):
    	super(PiServer,self).__init__(address, handler)
    	self.arduino = Arduino(9600)


if __name__ == "__main__":
	# host = raw_input("IP ?\n")
	# port = raw_input("PORT ?\n")

	host = "127.0.0.1"
	port = 4242

	server = PiServer((host, port), PiHandler)
	server.serve_forever()

