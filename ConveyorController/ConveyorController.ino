#include <Servo.h>
#include <arduino-timer.h>

#include "SerialReader.h"
#include "Config.h"

Servo servos[numServos];

Timer<20, millis, byte> timer; // Timer to allow for scheduling of tasks in non-blocking manner (see arduino-timer library)

void setup() {
  Serial.begin(115200); // Initialize the serial connection with a baud rate of 115200

  // Setup the servos. For each servo
  for (byte i = 0; i < numServos; i++) {
    servos[i].attach(servoPinNums[i]);                          // attach to the corresponding pin
    servos[i].write(closedAngles[i%2] + armClosedAngleOffset[i]); // move the arm to the closed position
    timer.in(SERVO_TRAVEL_TIME, killServo, i);                  // set task to kill the servo once it arrives in the correct position
  }
}

// Function to open and then close a given flipper. Assumes the
// given servo is detached at function start and so reattaches
// before sending the command to open and sets timer to close after
// allotted time. The function is sometimes called by the timer and
// so must return a boolean to indicate if it should be repeated, thus
// it always returns false. Returning false may not be strictly necessary
// as it should always be called by in, which shouldn't repeat, but
// better safe than sorry.
bool cycleArm(byte servoNum) {
  // Check that flipper number is valid
  if (servoNum < 0 || servoNum >= numServos) return false;

  servos[servoNum].attach(servoPinNums[servoNum]); // attach the servo to the appropriate pin
  servos[servoNum].write(openAngles[servoNum%2]+armOpenAngleOffset[servoNum]);  // command servo to open angle
  timer.in(TIME_OPEN+SERVO_TRAVEL_TIME, closeArm, servoNum);  // schedule the servo to close at the appropriate time
  return false; // don't repeat if called by timer
}

// Sends signal to close the given flipper and then kills the
// servo after the SERVO_TRAVEL_TIME
bool closeArm(byte servoNum) {
  // Ensure the variable is valid, do nothing otherwise.
  if (servoNum < 0 || servoNum >= numServos) return false;
  
  servos[servoNum].write(closedAngles[servoNum%2] + armClosedAngleOffset[servoNum]);
  timer.in(SERVO_TRAVEL_TIME, killServo, servoNum);
  return false;
}

// Detaches from the given servo so we stop sending signals to it.
// The servos selected for this project simply don't engage the
// motor if no signal is given. Not the case with all servos,
// but fortunately the case with ours
bool killServo(byte servoNum) {
  // Ensure the variable is valid, do nothing otherwise.
  if (servoNum < 0 || servoNum >= numServos) return false;

  servos[servoNum].detach();
  return false;
}

void loop() {
  timer.tick(); // must be called to ensure proper function of timer
  SerialReader.receiveData();  // Looks for data from Serial
  if (SerialReader.hasMessage()) {  // if a whole message has been received from Serial,
    int servoNum = atoi(SerialReader.getMessage()); // convert the message to an int (assume it's the number of a servo to move)
    
    short waitTime = (servoNum/2) * WINDOW_TRAVEL_TIME - PRESWING + INITIAL_WAIT; // calculate the amount of time the arm has to wait to swing
    if (waitTime <= 0) { // If the wait time is negative
      cycleArm(servoNum); // cycle the given servo number right away
    }
    else {
      timer.in(waitTime, cycleArm, servoNum); // Otherwise wait the allotted time and then cycle the arm
    }
  }
}
