//Librairies
#include <AFMotor.h>
#include <Servo.h>

// Constants
int const DEFAULT_SENSOR = 12;
int const DEFAULT_RIGHT = 2;
int const DEFAULT_LEFT = 1;
int const DEFAULT_SERVO = 9;

int const DEFAULT_SPEED = 200;

int const SERVO_OFFSET = 81; // NOT SURE THIS IS THE EXACT VALUE. Must take better measurements
int const CLEAR_DISTANCE = 20;

volatile unsigned int leftTicks = 0;
volatile unsigned int rightTicks = 0;
volatile int leftTime = 0;
volatile int rightTime = 0;
const int INT_DELAY = 50;

bool const DEBUG = false;
bool const DETAIL_DEBUG = false;

////////////
// TODO : Fix a bug with distance measurement between -30° and -14° (at least)
// EDIT : This bug disappears sometimes ... Maybe it has something to do with power ? Not sure.
///////////

// Main Class : Car
class Car
{
public:
  static int DefaultSpeed;
  static int ClearDistance;

  Car(int rightMotor = DEFAULT_RIGHT, int leftMotor = DEFAULT_LEFT,
  int aServo = DEFAULT_SERVO, int aSensor = DEFAULT_SENSOR) :
  sensorPin(aSensor), right(AF_DCMotor(rightMotor)),
  left(AF_DCMotor(leftMotor))
  {
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

    // putting servo at an extreme, in prevision of a "servoSweep"
    SetServo(-45);
  };

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
    right.setSpeed(rightSpeed);
    left.setSpeed(leftSpeed);
  };

  void TurnAngle(int angle)
  {
    // 1 / ANGULAR SPEED ...~
    // THIS IS AN APPROXIMATION ! (and a bad one)
    float Alpha = rightSpeed/19;

    if (angle>0)
    {
      TurnRight();
      delay(angle*Alpha);
      ReleaseMotors();
    }
    else
    {
      TurnLeft();
      delay(-angle*Alpha);
      ReleaseMotors();
    }
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

  void Run()
  {
    //RESET minDist
    minDist = 1024;

    // ATTENTION !
    // THE FOLLOWING ALGORITHM IS TEMPORARY.

    // We sweep the servo (which gives some important values : means, minimum distance, ...)
    SweepServo();
    Serial.println(distances[45]);
    // If the distance in front of the car
    if (distances[45] < CLEAR_DISTANCE)
    {
      Serial.println("BELOW CLEAR DIST");
      Serial.println(minDist);

      //We put the servo at the center of the car
      SetServo(0);
      delay(200);

      // And we turn the servo in the right direction (left or right, depending on the sensed distances)
      // until the distance in front of the car is clear
      while (GetDistance() < CLEAR_DISTANCE)
      {
        if (leftMean > rightMean)
        {
          Serial.println("Turning left");
          TurnLeft();
          delay(100);
        }
        else
        {
          Serial.println("Turning right");
          TurnRight();
          delay(100);
        }
      }
    }
    Forward();
  };


  void RunAlt()
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
 /*
  void Follow()
  {
    while (GetDistance() > 20)
    {
      Forward();
      delay(3);
      Serial.print("Moving : ");
      Serial.println(GetDistance());
    }

    ReleaseMotors();

    while (GetDistance() < 25)
    {
      Serial.print("Stopped : ");
      Serial.println(GetDistance());
      delay(3);
    }


  }*/

  void RunStraight(unsigned int ticks)
  {
    // We reset right and left ticks
    rightTicks = 0;
    leftTicks = 0;
    
    leftTicks = 0;
    rightTicks = 0;
    Forward();
    while ( leftTicks < ticks and rightTicks < ticks )
    {
      float leftMedium = (float)leftTicks/(leftTicks + rightTicks);
      float rightMedium = (float)leftTicks/(leftTicks + rightTicks);
      
      if (leftMedium < rightMedium)
      {
        rightSpeed--;
        right.setSpeed(rightSpeed);
      }
      else
      {
        leftSpeed++;
        left.setSpeed(leftSpeed);
      }
    }
    //Serial.println("End");

    ReleaseMotors();

  }

  void Remote()
  {
    static int running = 0;
    static int turning = 0;
    static int sweep = 0;

    static const int RUN_FORWARD = 1;
    static const int RUN_BACKWARD = -1;
    static const int TURN_RIGHT = 2;
    static const int TURN_LEFT = -2;
    static const int SWEEP_SERVO = 3;

    static const int STOP = 0;

    if (Serial.available() > 0)
    {
      char input[20];
      int i = 0;
      while (Serial.available() > 0)
      {
        input[i] = Serial.read();
        i++;
        // Delay to avoid skipping consecutive signal readings
        delay(5);
      }
      input[i] = '\0';
      
      int value = atoi(input);
      
      // FOR DEBUG ONLY
      //value = -2;

      switch (value)
      {
        case RUN_FORWARD: {
          Forward();
          break;
        }
        case RUN_BACKWARD: {
          Backward();
          break;
        }
        case TURN_RIGHT: {
          TurnRight();
          break;
        }
        case TURN_LEFT: {
          TurnLeft();
          break;
        }
        case SWEEP_SERVO : {
          AltSweepServo();
          
          // The serial communication pattern in this mode is:
          // ANGLE[newline]
          // DISTANCE[newline]
          
          Serial.println(0);
          Serial.println(distances[0+45]);

          Serial.println(-45);
          Serial.println(distances[-45+45]);

          Serial.println(45);
          Serial.println(distances[45+45]);
          break;
        }
        case STOP: {
          ReleaseMotors();
          break;
        }
      } // End of switch

    }// End of Serial reading
  }
  //////////////////////
  //    ATTRIBUTES   //
  ////////////////////

  AF_DCMotor right;
  AF_DCMotor left;
  Servo servo;
  int sensorPin;
  int leftSpeed;
  int rightSpeed;
  int distances[180];
  //For processing distances :
  int leftMean;
  int rightMean;
  int leftMaxAngle;
  int rightMaxAngle;
  int minDist;
};


//GLOBAL VARIABLES: Car
Car car;

void leftTick()
{
  if (millis() - leftTime > INT_DELAY)
  {
    leftTime = millis();
    leftTicks++;
  }
}

void rightTick()
{
  if (millis() - rightTime > INT_DELAY)
  {
    leftTime = millis();
    rightTicks++;
  }
}


void setup() {
  Serial.begin(9600);           // set up Serial library at 9600 bps

  car.AttachServo(9);

  car.SetSpeed(DEFAULT_SPEED);
  car.ReleaseMotors();
  car.SetServo(0);
  delay(200);

  attachInterrupt(3, leftTick, FALLING);
  attachInterrupt(5, rightTick, FALLING);

}

void loop()
{
  car.Remote();
}


