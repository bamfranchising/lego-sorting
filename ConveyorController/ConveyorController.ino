#include <Servo.h>
#include "SerialReader.h"
#include <arduino-timer.h>

#define FLIPPER_CLOSE 169 // Angle of the closed state of the servos
#define FLIPPER_OPEN 104  // Angle of the open state of the servos (crosses the entire conveyor belt)
#define TIME_OPEN 1500    // Time for the flipper to remain open after it has arrived
#define TRAVEL_TIME 150   // The time required for the flipper to travel between the closed and open states.

const byte numFlippers = 4;          // records the number of servos
byte servoPinNums[] = {4, 5, 6, 7};  // records the pin numbers of the servos
int8_t servoCloseOffset[] = {0, 0, -7, 5};  // amount the servo is offset in closed position. Larger = more counterclockwise
int8_t servoOpenOffset[] =  {0, 0, -7, 0};  // amount the servo is offset in open position. Larger = less open
Servo flippers[numFlippers];

Timer<20, millis, byte> timer; // Timer to allow for scheduling of tasks in non-blocking manner

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);

  for (byte i = 0; i < numFlippers; i++) {
    flippers[i].attach(servoPinNums[i]);
    flippers[i].write(FLIPPER_CLOSE + servoCloseOffset[i]);
    timer.in(TRAVEL_TIME, killServo, i);
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
bool cycleFlipper(byte flipperNum) {
  // Check that flipper number is valid
  if (flipperNum < 0 || flipperNum >= numFlippers) return false;

  flippers[flipperNum].attach(servoPinNums[flipperNum]); // attach the servo to the appropriate pin
  flippers[flipperNum].write(FLIPPER_OPEN+servoOpenOffset[flipperNum]);              // command servo to open angle
  timer.in(TIME_OPEN+TRAVEL_TIME, closeFlipper, flipperNum);  // schedule the servo to close at the appropriate time
  return false; // don't repeat if called by timer
}

// Sends signal to close the given flipper and then kills the
// servo after the TRAVEL_TIME
bool closeFlipper(byte flipperNum) {
  // Ensure the variable is valid, do nothing otherwise.
  if (flipperNum < 0 || flipperNum >= numFlippers) return false;
  // stepFlipper(flipperNum, FLIPPER_OPEN, FLIPPER_CLOSE);
  flippers[flipperNum].write(FLIPPER_CLOSE + servoCloseOffset[flipperNum]);
  timer.in(TRAVEL_TIME, killServo, flipperNum);
  return false;
}

// Detaches from the given servo so we sending signals to it.
// The servos selected for this project simply don't engage the
// motor if no signal is given. Not the case with all servos,
// but fortunately the case with ours
bool killServo(byte servoNum) {
  // Ensure the variable is valid, do nothing otherwise.
  if (servoNum < 0 || servoNum >= numFlippers) return false;
  flippers[servoNum].detach();
  return false;
}

void loop() {
  timer.tick(); // must be called to ensure proper function of timer
  SerialReader.receiveData();  // Looks for data from Serial
  if (SerialReader.hasMessage()) {  // if a whole message has been received from Serial,
    int flipperNum = atoi(SerialReader.getMessage()); // convert the message to an int (assume it's the number of a servo to move)
    cycleFlipper(flipperNum); // cycle the given servo number
  }
}
