#include "HMC5883L.h"

class Compass
{
  public:

    HMC5883L compass;
    int pin;

    Compass(int aPin) : pin(aPin)
    {
      compass= HMC5883L();
    }


    float ReadAngle(int n=1)
    {
      float headingDegrees = 0;
      for (int i = 0; i < n; i++)
      {
        // Retrive the raw values from the compass (not scaled).
        MagnetometerRaw raw = compass.ReadRawAxis();
        // Retrived the scaled values from the compass (scaled to the configured scale).
        MagnetometerScaled scaled = compass.ReadScaledAxis();

        // Calculate heading when the magnetometer is level, then correct for signs of axis.
        //float result = float(raw.YAxis)/float(raw.XAxis);
        float result = float(raw.YAxis)/float(raw.XAxis);
        float heading = atan2(float(scaled.YAxis),float(scaled.XAxis));

        // Your mrad result / 1000.00 (to turn it into radians).
        float declinationAngle = 0.0137;
        // If you have an EAST declination, use += declinationAngle, if you have a WEST declination, use -= declinationAngle
        heading += declinationAngle;

        // Correct for when signs are reversed.
        if(heading < 0.0)
          heading += 2*PI;

        // Check for wrap due to addition of declination.
        if(heading > 2*PI)
          heading -= 2*PI;

        // Convert radians to degrees for readability and add it to the mean
        headingDegrees += (heading * 180/M_PI)/n; 
      }

      //  if (pos%50==0)
      //Output(raw, scaled, heading, Average());
      return headingDegrees;
    }


    void init()
    {    
      Serial.println("Setting scale to +/- 1.3 Ga");
      int error = compass.SetScale(1.3); // Set the scale of the compass.
      if(error != 0) // If there is an error, print it out.
        Serial.println(compass.GetErrorText(error));

      Serial.println("Setting measurement mode to continuous.");
      error = compass.SetMeasurementMode(Measurement_Continuous); // Set the measurement mode to Continuous
      if(error != 0) // If there is an error, print it out.
        Serial.println(compass.GetErrorText(error));
    }

    void Output(MagnetometerRaw raw, MagnetometerScaled scaled, float heading, float headingDegrees)
    {
      Serial.print("Raw:\t");
      Serial.print(raw.XAxis);
      Serial.print("   ");   
      Serial.print(raw.YAxis);
      Serial.print("   ");   
      Serial.print(raw.ZAxis);
      Serial.print("   \tScaled:\t");

      Serial.print(scaled.XAxis);
      Serial.print("   ");   
      Serial.print(scaled.YAxis);
      Serial.print("   ");   
      Serial.print(scaled.ZAxis);

      Serial.print("   \tHeading:\t");
      Serial.print(heading);
      Serial.print(" Radians   \t");
      Serial.print(headingDegrees);
      Serial.println(" Degrees   \t");
    }

};
