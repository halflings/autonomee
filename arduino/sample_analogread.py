import time
from pyfirmata import ArduinoMega, util

pin = 11

board = ArduinoMega('/dev/ttyACM0')

analog = board.get_pin('a:12:o')
while True:
    print analog.write(142)
    time.sleep(0.5)
