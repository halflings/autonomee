from arduino import Arduino
from time import sleep

if __name__=="__main__":
    arduino = Arduino(9600)

    while True:
        arduino.analogRead(11)
        sleep(1)