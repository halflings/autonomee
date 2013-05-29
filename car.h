//Librairies
#include "AFMotor.h"

#include "Servo.h"
#include <Wire.h>
#include "compass.h"
// Constants
int const DEFAULT_SENSOR = 14;
int const DEFAULT_RIGHT = 2;
int const DEFAULT_LEFT = 1;
int const DEFAULT_SERVO = 9;

int const COMPASS_PIN = 0;
int const THERMOMETER_PIN = 2;

int const DEFAULT_SPEED = 200;

int const SERVO_OFFSET = 81; // NOT SURE THIS IS THE EXACT VALUE. Must take better measurements
int const CLEAR_DISTANCE = 20;

// States
int const STATE_VOID = 0;
int const STATE_FORWARD = 1;
#define STATE_BACKWARD −1
int const STATE_RIGHT = 2;
int const STATE_LEFT = -2;



bool const DEBUG = false;
bool const DETAIL_DEBUG = false;

#define TEMPERATURE_PRECISION 9
#define DEFAULT_PIN 3
#include "OneWire.h"
#include "DallasTemperature.h"



OneWire oneWire(THERMOMETER_PIN);

// Pass our oneWire reference to Dallas Temperature. 
DallasTemperature sensors(&oneWire);
class Thermometer
{
  public:

    // Setup a oneWire instance to communicate with any OneWire devices (not just Maxim/Dallas temperature ICs)
    //OneWire oneWire;
    
    // Pass our oneWire reference to Dallas Temperature. 
    //DallasTemperature sensors;
    int pin;
    int numberOfDevices; // Number of temperature devices found
    
    DeviceAddress tempDeviceAddress; // We'll use this variable to store a found device address


    Thermometer(int aPin) : pin(aPin)//, oneWire(aPin),sensors(&oneWire)
    {

    }
   /*~Thermometer()
   {
     delete oneWire;
     delete sensors;
   }
    */
    void init()
    {
      // start serial port
      Serial.println("Dallas Temperature IC Control Library Demo");
    
      // Start up the library
      sensors.begin();
      
      // Grab a count of devices on the wire
      numberOfDevices = sensors.getDeviceCount();
      
      // locate devices on the bus
      Serial.print("Locating devices...");
      
      Serial.print("Found ");
      Serial.print(numberOfDevices, DEC);
      Serial.println(" devices at pin");
      Serial.println(pin);
    
      // report parasite power requirements
      Serial.print("Parasite power is: "); 
      if (sensors.isParasitePowerMode()) Serial.println("ON");
      else Serial.println("OFF");
      
      // Loop through each device, print out address
      for(int i=0; i < numberOfDevices; i++)
      {
        // Search the wire for address
        if(sensors.getAddress(tempDeviceAddress, i))
    	{
    		Serial.print("Found device ");
    		Serial.print(i, DEC);
    		Serial.print(" with address: ");
    		printAddress(tempDeviceAddress);
    		Serial.println();
    		
    		Serial.print("Setting resolution to ");
    		Serial.println(TEMPERATURE_PRECISION, DEC);
    		
    		// set the resolution to TEMPERATURE_PRECISION bit (Each Dallas/Maxim device is capable of several different resolutions)
    		sensors.setResolution(tempDeviceAddress, TEMPERATURE_PRECISION);
    		
    		 Serial.print("Resolution actually set to: ");
    		Serial.print(sensors.getResolution(tempDeviceAddress), DEC); 
    		Serial.println();
    	}else{
    		Serial.print("Found ghost device at ");
    		Serial.print(i, DEC);
    		Serial.print(" but could not detect address. Check power and cabling");
    	}
      }
    
    }
    
    // function to print the temperature for a device
    float ReadTemperature(DeviceAddress deviceAddress)
    {
      // method 1 - slower
      //Serial.print("Temp C: ");
      //Serial.print(sensors.getTempC(deviceAddress));
      //Serial.print(" Temp F: ");
      //Serial.print(sensors.getTempF(deviceAddress)); // Makes a second call to getTempC and then converts to Fahrenheit
    
      // method 2 - faster
      return sensors.getTempC(deviceAddress);
      /*Serial.print("Temp C: ");
      Serial.print(tempC);
      Serial.print(" Temp F: ");
      Serial.println(DallasTemperature::toFahrenheit(tempC)); // Converts tempC to Fahrenheit*/
    }
    
    float nothing()
    { 
      // call sensors.requestTemperatures() to issue a global temperature 
      // request to all devices on the bus
      //Serial.print("Requesting temperatures...");
      sensors.requestTemperatures(); // Send the command to get temperatures
     // Serial.println("DONE");
      
      
      // Loop through each device, print out temperature data
      for(int i=0;i<numberOfDevices; i++)
      {
        // Search the wire for address
        if(sensors.getAddress(tempDeviceAddress, i))
    	{
    		// Output the device ID
    		//Serial.print("Temperature for device: ");
    		//Serial.print(i,DEC);
    		
    		// It responds almost immediately. Let's print out the data
    		return ReadTemperature(tempDeviceAddress); // Use a simple function to print out the data
    	} 
    return(0);
    	//else ghost device! Check your power requirements and cabling
    	
      }
    }
    
    // function to print a device address
    void printAddress(DeviceAddress deviceAddress)
    {
      for (uint8_t i = 0; i < 8; i++)
      {
        if (deviceAddress[i] < 16) Serial.print("0");
        Serial.print(deviceAddress[i], HEX);
      }
    }
};


// Main Class : Car
class Car
{
public:
  static int DefaultSpeed;
  static int ClearDistance;

  Car() : 
  sensorPin(DEFAULT_SENSOR), right(AF_DCMotor(DEFAULT_RIGHT)),
  left(AF_DCMotor(DEFAULT_LEFT)), compass(COMPASS_PIN), x(0), y(0), avgSpeed(0), thermometer(THERMOMETER_PIN), state(STATE_VOID)
  {
    // all the initialization is done in "init()"
  };

  void init() {
    // initializing the compass
    compass.init();

    // initializing the compass
    thermometer.init();
    //servo.attach(aServo);
    leftSpeed = DEFAULT_SPEED;
    rightSpeed = DEFAULT_SPEED;
    SetSpeed(DEFAULT_SPEED);
    ReleaseMotors();

    //for processing distances
    leftMean = 0;
    rightMean = 0;
    leftMaxAngle = 0;
    rightMaxAngle = 0;

    // Min as max possible value
    minDist = 1024;

    // initializing distances :
    for (int i = 0 ; i<= 180; i++)
    {
      distances[i] = 0;
    }

    // putting servo at the center
    SetServo(0);
  }

  // FOR DEBUG ONLY... it seems the servo need to be attached in setup
  // This is weird. Check if it can be done earlier
  void AttachServo(int pin)
  {
    servo.attach(pin);
  }

  //SENSOR RELATED

  int GetDistance()
  {
    return analogRead(sensorPin);
  };

  // SERVO RELATED

  void SetServo(int angle)
  {
    servo.write(SERVO_OFFSET - angle);
  }

  int ReadServo()
  {
    return (SERVO_OFFSET - servo.read());
  }

  void AltSweepServo()
  {
    SetServo(-45);
    delay(150);
    distances[-45+45] = GetDistance();

    SetServo(0);
    delay(150);
    distances[0+45] = GetDistance();

    SetServo(45);
    delay(150);
    distances[45+45] = GetDistance();

  }

  void SweepServo()
  {


    if (ReadServo() == -45)
    {
      for ( int angle = -45; angle <= 45; angle++)
      {
        SetServo(angle);
        delay(5);
        distances[angle+45] = GetDistance();
      }
    }
    else
    {
      SetServo(45);
      delay(5);
      for ( int angle = 45; angle >= -45; angle--)
      {
        SetServo(angle);
        distances[angle+45] = GetDistance();
        delay(5);
      }
    }

    ProcessDistances();

    //FOR DEBUG ONLY
    if (DETAIL_DEBUG)
    {
      for (int angle = -45; angle <= 45; angle += 5)
      {
        for (int i = 0; i<(distances[angle+45]/4); i++)
        {
          Serial.print(" ");
        }
        Serial.print("| : ");
        Serial.print(angle);
        Serial.print(" degrees ; ");
        if (minDist == distances[angle + 45])
        {
          Serial.print("MIN! ");
        }
        if (angle == leftMaxAngle)
        {
          Serial.print("LEFT MAX! ");
        }
        else if (angle == rightMaxAngle)
        {
          Serial.print("RIGHT MAX! ");
        }
        Serial.println(" ");
      }
    }
  }

  void Forward()
  {
    right.run(FORWARD);
    left.run(FORWARD);
  };

  void Backward()
  {
    right.run(BACKWARD);
    left.run(BACKWARD);
  };

  void ReleaseMotors()
  {
    right.run(RELEASE);
    left.run(RELEASE);
  };

  void Right()
  {
    right.run(FORWARD);
    left.run(RELEASE);
  };

  void Left()
  {
    right.run(RELEASE);
    left.run(FORWARD);
  };

  void TurnRight()
  {
    ReleaseMotors();
    right.run(BACKWARD);
    left.run(FORWARD);
  }

  void TurnLeft()
  {
    ReleaseMotors();
    right.run(FORWARD);
    left.run(BACKWARD);
  }

  void SetSpeed(int aSpeed)
  {
    leftSpeed = aSpeed;
    rightSpeed = aSpeed;
    UpdateSpeed();
  };

  void UpdateSpeed()
  {
    // Protected UpdateSpeed: max speed: 250, min speed: 0

    if (rightSpeed <= 250 && rightSpeed >= 0)
    {
      right.setSpeed(rightSpeed);
    }
    else
    {
      Serial.print("Speed overflow : ");
      Serial.println(rightSpeed);
      right.setSpeed(250);
    }

    if (leftSpeed <= 250 && leftSpeed >= 0)
    {
      left.setSpeed(leftSpeed);
    }
    else
    {
      Serial.print("Speed overflow : ");
      Serial.println(leftSpeed);
      left.setSpeed(250);
    }
  };

  void TurnTo(float goal)
  {
    static float angleEpsilon = 2;
    float curAngle = compass.ReadAngle(5);

    float goalAngle = goal;

    float delta = min( abs(curAngle - goalAngle), abs(curAngle  - (goal + 360) ) );

    while (delta > angleEpsilon)
    {
      
      if ( abs(curAngle  - (goal + 360) ) < abs(curAngle - goal) )
        goalAngle = goal + 360;
      else
        goalAngle = goal;


      // TODO : Add test to turn to the closest direction (right or left)
      curAngle = compass.ReadAngle(5);
      delta = min( abs(curAngle - goalAngle), abs(curAngle  - (goal + 360) ) );

      Serial.print("angle = ");
      Serial.println(curAngle);
      Serial.print("delta = ");
      Serial.println(delta);
      Serial.print("Condition : ");
      Serial.println(delta > angleEpsilon);

      if (goalAngle > curAngle)
        TurnRight();
      else
        TurnLeft();

      int duration = 5 + round(300 * ((float) delta/180.0));
      int start = millis();
      Serial.println(duration);
      while (millis() - start < duration && delta > angleEpsilon)
      {
        curAngle = compass.ReadAngle(5);
        delta = min( abs(curAngle - goalAngle), abs(curAngle  - (goal + 360) ) );
      }

      ReleaseMotors();
      delay(400);
    }

    ReleaseMotors();
  }


  int ProcessDistances()
  {
    rightMean = 0;
    leftMean = 0;

    int rightMax = 0;
    int leftMax = 0;

    bool right = false;
    bool left = false;

    minDist = 1024;

    for (int i=-45 ; i<45; i++)
    {
      int dist = distances[i+45];

      left = i <= -10;
      right = i >= 10;
      if (right)
      {
        rightMean += dist;
        if (dist > rightMax)
        {
          rightMax = dist;
          rightMaxAngle = i;
        }
      }
      else if (left)
      {
        leftMean += dist;
        if (dist > leftMax)
        {
          leftMax = dist;
          leftMaxAngle = i;
        }
      }

      minDist = dist < minDist ? dist : minDist;
    }

    rightMean /= 36;
    leftMean /= 36;

  }

  // BEHAVIOR RELATED

  void RandomRun()
    // When the car encounters an obstacle, turns right until
    // there's no obstacle ahead
  {
    Forward();

    if (GetDistance() < CLEAR_DISTANCE)
    {

      ReleaseMotors();

      // And we turn the servo in the right direction (left or right, depending on the sensed distances)
      // until the distance in front of the car is clear
      TurnRight();
      while (GetDistance() < CLEAR_DISTANCE)
      {
        delay(10);
      }
    }

  }

  void Feedback() {

    Serial.print(" Angle : ");
    Serial.print(compass.ReadAngle());
    
    Serial.print(" Temperature : ");
    Serial.print(thermometer.nothing());
    
    Serial.print(" | Distance : ");
    Serial.print(GetDistance());

    Serial.print(" | Speed : ");
    Serial.print(avgSpeed);
    
    Serial.print(" | Position : (");
    Serial.print(x);
    Serial.print(", ");
    Serial.print(y);
    Serial.print(")");
    
    Serial.println(" ");

  }

  void Remote()
  {
    static int running = 0;
    static int turning = 0;
    static int sweep = 0;

    static const int RUN_BACKWARD = -1;
    static const int STOP = 0;
    static const int RUN_FORWARD = 1;
    static const int TURN_RIGHT = 2;
    static const int TURN_LEFT = -2;
    static const int SWEEP_SERVO = 3;
    static const int TURN_SERVO = 4;
    static const int SET_SPEED = 5;


    if (Serial.available() > 0)
    {
      char input[17];
      int i = 0;
      while ((Serial.available() > 0) && (i<16))
      {
        input[i] = Serial.read();
        i++;
        // Delay to avoid skipping consecutive signal readings
        delay(5);
      }
      input[i] = '\0';
      String inputStr(input);

      int operation = inputStr.substring(0,2).toInt();
      int operand1 = inputStr.substring(3,9).toInt();
      int operand2 = inputStr.substring(10,16).toInt();

      switch (operation)
      {
      case RUN_FORWARD: 
        {
          //leftSpeed = operand1;
          //rightSpeed = operand2;
          //UpdateSpeed();

          Forward();
          state = STATE_FORWARD;
          break;
        }
      case RUN_BACKWARD: 
        {
          //leftSpeed = operand1;
          //rightSpeed = operand2;
          //UpdateSpeed();
          state = -1;
          Backward();
          break;
        }
      case TURN_RIGHT: 
        {
          state = STATE_RIGHT;
          TurnRight();
          break;
        }
      case TURN_LEFT: 
        {
          state = STATE_LEFT;
          TurnLeft();
          break;
        }
      case SWEEP_SERVO : 
        {
          AltSweepServo();

          // The serial communication pattern in this mode is:
          // ANGLE[newline]
          // DISTANCE[newline]

          Serial.print("ANGLE : -45 | DISTANCE : ");
          Serial.println(distances[-45+45]);

          Serial.print("ANGLE : 0 | DISTANCE : ");
          Serial.println(distances[0+45]);

          Serial.print("ANGLE : 45 | DISTANCE : ");
          Serial.println(distances[45+45]);
          break;
        }
      case TURN_SERVO : 
        {
          SetServo(operand1);
          break;
        }
      case SET_SPEED :
        {
          SetSpeed(operand1);
          break;
        }
      case STOP: 
        {
          state = STATE_VOID;
          ReleaseMotors();
          break;
        }
      } // End of switch

    }// End of Serial reading
  }

  void ApplyState()
  {
    switch (state) {

      case STATE_FORWARD:
      {
        if (GetDistance() < 20)
        {
          TurnRight();
        }
        else
        {
          Forward();
        }

        break;
      }

      
    }
  }
  //////////////////////
  //    ATTRIBUTES   //
  ////////////////////

  AF_DCMotor right;
  AF_DCMotor left;
  Servo servo;
  Compass compass;
  int sensorPin;
  int leftSpeed;
  int rightSpeed;
  int distances[180];
  
  Thermometer thermometer;
  //For processing distances :
  int leftMean;
  int rightMean;
  int leftMaxAngle;
  int rightMaxAngle;
  int minDist;
  int state;

  int x;
  int y;
  float avgSpeed;
};

#include "OneWire.h"
#include <DallasTemperature.h>

// Data wire is plugged into port 2 on the Arduino
#define TEMPERATURE_PRECISION 9
#define DEFAULT_PIN 3


