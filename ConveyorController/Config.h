// File where we can configure the arm angle offsets and pin numbers seperate from the 
// main block of code.
#ifndef PIN_AND_ANGLE_CONFIG
#define PIN_AND_ANGLE_CONFIG

#define RIGHT_ARM_CLOSE_ANGLE 169 // Angle of the closed state of the servos on the right side
#define RIGHT_ARM_OPEN_ANGLE 104  // Angle of the open state of the servos on the right side (crosses the entire conveyor belt)
#define LEFT_ARM_CLOSE_ANGLE 10    //Angle of the closed state of the servos on the left side
#define LEFT_ARM_OPEN_ANGLE 78    //Angle of the open state of the servos on the left side.    
#define TIME_OPEN 1300          // Time for the arm to remain open after it has arrived
#define SERVO_TRAVEL_TIME 150   // The time required for the arm to travel between the closed and open states.
#define BELT_SPEED 17           // Speed of the conveyor belt in cm/s
#define ARM_LENGTH 28           // Distance between each arm in cm
#define WINDOW_TRAVEL_TIME ((int)ARM_LENGTH*1000/BELT_SPEED)  // Amount of time it takes for a piece to travel the length of a segment in ms
#define PRESWING 100            // Arms swing out early by this amount in ms
#define INITIAL_WAIT ((int)19 * 1000/BELT_SPEED)

#define DROPPER_PIN 12
#define DROPPER_CLOSED 0
#define DROPPER_OPEN 50

// There are two different sides the servos are on. We assume the perspective of looking down the conveyor belt
// in the direction it is moving. Thus, the servos on the right must swing clockwise (as viewed from above) to
// move across the belt, with the servos on the left moving counterclockwise.

// The servos are numbered as such:
// 0 | 1
// 2 | 3
// 4 | 5
// 6 | 7
//  \/

const byte numServos = 8;          // records the number of servos
const byte servoPinNums[] = {11, 7, 10, 6, 9, 5, 8, 4};  // records the pin numbers of the servos
const byte openAngles[] = {RIGHT_ARM_OPEN_ANGLE, LEFT_ARM_OPEN_ANGLE};
const byte closedAngles[] = {RIGHT_ARM_CLOSE_ANGLE, LEFT_ARM_CLOSE_ANGLE};
// Angle offsets for the closed and open positions. Generally the same for both. For the right side
// (looking down the conveyor belt) larger numbers means more closed. The opposite is true for the left side
const int8_t armClosedAngleOffset[] = {5, 0, -5, -5, 0, -5, 0, 0};  // amount the servo is offset in closed position. Larger = more counterclockwise
const int8_t armOpenAngleOffset[] =  {0, 0, -5, -5, 0, -5, 0, 0};  // amount the servo is offset in open position. Larger = more counterclockwise
#endif