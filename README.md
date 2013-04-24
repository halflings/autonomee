# Carosif (temporary name)

A Python front-end for robot localization (and other uses) using SVG for maps' representation and Qt for the UI.

You can also check the robot's arduino sketch, __AutoRobot.ino__. 

## Features

* A *really* basic SVG parser
* A pathfinder (A\*)
* Nearest obstacle detection (to simulate the sensor's measurements)
* Basic probability model : particle filter. (hopefully we'll also implement one based on Kalman's filter)
* Visualization of the robot's movements and a 'heatmap' of the probabilities.

## Dependencies

* Python 2.7
* Qt and PySide (Qt's python binding)
* numpy
* PySerial
* scipy

## Important

This is a work in progress and the code base can change very radically. Don't except (for now) something working out of the box  !

## Updates :

### March-2013

This now also includes a server/client made to be used in a Raspberry Pi connected to the Arduino controlling the car. Check how that work out in a 'joystick controlled' mode :

https://www.youtube.com/watch?v=rbX47X8HtGU
