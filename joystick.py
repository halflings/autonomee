import sfml as sf
import time

if sf.Joystick.isConnected(0):
    print sf.Joystick.getAxisPosition(0, sf.Joystick.Y)
    time.sleep(1)