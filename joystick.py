#!/usr/bin/env python

import pygame
from time import sleep
import serial
import sys
import os
#from pygame import joystick, event

ser = serial.Serial('/dev/ttyACM0', 9600)
pygame.init()
#joystick.init()
j = pygame.joystick.Joystick(0)
j.init()
print 'Initialized Joystick : {}'.format(j.get_name())


try:
    while True:

        sum = 0

        while j.get_axis(1) != 0 and j.get_button(11) != 0:
            sum += j.get_axis(1)/4
            sleep(0.02)
            pygame.event.pump()


        if sum != 0:
            data = "{}".format(abs(int(sum*100)))
            print "SENT {}".format(data)
            ser.write(data)

        pygame.event.pump()
        # for i in range(0, j.get_numaxes()):
        #     if j.get_axis(i) != 0.00:
        #         print 'Axis %i reads %.2f' % (i, j.get_axis(i))
        # for i in range(0, j.get_numbuttons()):
        #     if j.get_button(i) != 0:
        #         print 'Button %i reads %i' % (i, j.get_button(i))

        sleep(0.1)

except KeyboardInterrupt:
    j.quit()
    ser.exit()