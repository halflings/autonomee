//Librairies
#include <Arduino.h>
#include <Wire.h>
#include "car.h"

volatile unsigned int leftTicks = 0;
volatile unsigned int rightTicks = 0;
volatile int leftTime = 0;
volatile int rightTime = 0;

const int INT_DELAY = 50;
const int UPDATE_T = 400;
const float TICK_TO_MM = 1;

const int RIGHT_INT = INT5;
const int LEFT_INT = INT4;

Car car;

void leftWheel()
{

  if (millis() - leftTime > INT_DELAY)
  {
    leftTime = millis();
   // Serial.println("c");
    leftTicks++;
  }
}

void rightWheel()
{

  if (millis() - rightTime > INT_DELAY)
  {
    leftTime = millis();
   // Serial.println("d");
    rightTicks++;
  }
}

float degToRad(float deg)
{
  return deg / 180 * M_PI;
}

void updateCar()
{
  // We consider that the car have moved straight for the min
  // of the two ticks, and then just rotated
  int distance = max(leftTicks, rightTicks) * TICK_TO_MM;
  //Serial.println(distance);
  car.avgSpeed = distance / (UPDATE_T/100);
  //Serial.println(car.avgSpeed);
  float dir = degToRad(car.compass.ReadAngle());
  car.x += distance * cos(M_PI - dir);
  car.y += distance * sin(M_PI - dir);

  leftTicks = 0;
  rightTicks = 0;
}

void setup()
{
  // Set up Serial library at 9600 bps
  Serial.begin(9600);
  Wire.begin();

  attachInterrupt(RIGHT_INT, rightWheel,FALLING);
  attachInterrupt(LEFT_INT, leftWheel,FALLING);

  car.init();
  car.AttachServo(9);

  car.SetSpeed(DEFAULT_SPEED);
  car.ReleaseMotors();
  car.SetServo(0);
  delay(200);

}

void loop()
{

  //Serial.println(car.compass.ReadAngle());
  //car.Forward();
  
  static long lastT = 0;
  
  if ( (millis() - lastT) > UPDATE_T )
  {
    lastT = millis();
    updateCar();
  }

  // Reads from the serial, can change the car's state
  car.Remote();

  // Performs the operations related to the car's current state
  car.ApplyState();

  // Writes information about the car (temperature, speed, ...) on the serial
  car.Feedback();
  
}


