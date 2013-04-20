#!/usr/bin/env python

"""
    joystick.py - work in progress : joystick class.
"""

import pygame
from time import sleep
import serial
# import sys
# import os

#from pygame import joystick, event

ser = serial.Serial('/dev/ttyACM0', 9600)
pygame.init()
pygame.joystick.init()
j = pygame.joystick.Joystick(0)
j.init()
print 'Initialized Joystick : {}'.format(j.get_name())


running = False
turning = False


try:
    while True:

        sum = 0

        axisX = j.get_axis(1)
        axisY = j.get_axis(0)

        if axisX != 0 and not running:
            running = True

            if axisX > 0:
                ser.write('-1')
            else:
                ser.write('1')

        if axisY != 0 and not turning:
            turning = True

            if axisY > 0:
                ser.write('2')
            else:
                ser.write('-2')

        if (axisX == 0 and running) or (axisY == 0 and turning):
            ser.write('0')
            turning = False
            running = False

        pygame.event.pump()


except KeyboardInterrupt:
    j.quit()
    ser.exit()