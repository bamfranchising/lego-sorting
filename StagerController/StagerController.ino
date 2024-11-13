#include <Servo.h>
#include <arduino-timer.h>



// Define the angles of the left and right positions of the flipper servo
#define FLIPPER_LEFT 50
#define FLIPPER_RIGHT 130

// Define the open and closed angles of the gate servos
#define GATE_OPEN 180
#define GATE_CLOSE 105

// Define the pins of the servos
#define FLIPPER_PIN 9
#define LEFT_GATE_PIN 10
#define RIGHT_GATE_PIN 11

// Define the pins of the drop triggering button
#define DROP_PIECE_PIN 3

// Define pin of the IR sensor
#define IR_SENSOR_PIN 5
#define IR_SENSOR_PIN2 7

// Define pin for turning off vibration
#define V_PIN 36

// Define variables for the various servos and states
Servo flipper;
bool flipperLeft;
Servo gateLeft;
bool leftHasItem;
Servo gateRight;
bool rightHasItem;

// bool to track if we're waiting to reactiveate the IR sensor
volatile bool bouncing = false;

// bool to track if we're waiting to reactivate the drop pin
volatile bool drop_bouncing = false;

// bool to track if vibration is on
volatile bool v_on = true;

// create timer to handle waiting while not blocking
auto timer = timer_create_default();
Timer<2, millis, Servo> closetimer;

void turnVibrationOff() {
  v_on = false;
  digitalWrite(V_PIN, HIGH);
}

void turnVibrationOn() {
  v_on = true;
  digitalWrite(V_PIN, LOW);
}


void receiveItem() {
  // if both bins are occupied, drop the piece in the current bin
  if(rightHasItem && leftHasItem) {
    Serial.println("Both bins occupied, dumping extra piece in current bin");
    return;
  }
  // One bin is free, assume it's the one we're currently dumping pieces into
  if (flipperLeft) {
    leftHasItem = true;
    flipper.write(FLIPPER_RIGHT);
    Serial.println("Left bin now has item");
  }
  else {
    rightHasItem = true;
    timer.in(100, [](void*)->bool { flipper.write(FLIPPER_LEFT); return false;});
    Serial.println("Right bin now has item");
  }
  flipperLeft = !flipperLeft;
  if (rightHasItem && leftHasItem) {
    // turn off vibration
    turnVibrationOff();
  }
}

void openGate(Servo gate, bool& hasItem) {
  gate.write(GATE_OPEN);
  hasItem = false;
  closetimer.in(500, closeGate, gate);
}

bool closeGate(Servo gate) {
  gate.write(GATE_CLOSE);
  return false;
}

// function called when the DROP_PIECE_PIN goes high
// or a timer calls it
void dropItem() {
//  Serial.println("Dropping item...");

  if (drop_bouncing) return;
  drop_bouncing = true;
  
  timer.in(500, [](void*) -> bool {drop_bouncing = false; return false;});

  // if both bins are occupied or neither bin is occupied, drop items out of the one where the flipper is pointing
  if ((leftHasItem && rightHasItem) || (!leftHasItem && !rightHasItem)) {
    if (flipperLeft) { // flipper is pointing to the left, so open the left gate
      openGate(gateLeft, leftHasItem);
    }
    else { // flipper is poing to the right, open the right gate
      openGate(gateRight, rightHasItem);
    }
  }
  // otherwise one bin has an item and we should open that bin
  else{
    if (leftHasItem) {
      openGate(gateLeft, leftHasItem);
//      Serial.println("Item dropped from left bin");
    }
    else {
      openGate(gateRight, rightHasItem);
//      Serial.println("Item dropped from right bin");
    }
  }
  if (!v_on) {
    // turn on the vibration
    turnVibrationOn();
  }
//  else {
////    Serial.println("No item available to drop");
//  }
}

// function called when the IR beam is broken
void beamBreak() {
  // check if the beam was broken recently
  if (!bouncing) {
    Serial.println("Receiving item...");
    receiveItem();

    // tell everyone the beam was broken recently
    bouncing = true;

    // reset the variable in 200ms
    timer.in(200, [](void*) -> bool {bouncing = false; return false;});
  }
}

void setup() {
  Serial.begin(115200);
  // Attach the servos on the various pins
  flipper.attach(FLIPPER_PIN);  
  gateLeft.attach(LEFT_GATE_PIN);
  gateRight.attach(RIGHT_GATE_PIN);

  // Put the flipper servo and state into a starting configuration
  flipper.write(FLIPPER_LEFT);
  flipperLeft = true;

  // Start both bins closed and empty
  gateLeft.write(GATE_CLOSE);
  gateRight.write(GATE_CLOSE);
  leftHasItem = false;
  rightHasItem = false;

  // Setup the input pins for the drop button
  pinMode(DROP_PIECE_PIN, INPUT);

  // Setup the input pin for the IR sensor
  pinMode(IR_SENSOR_PIN, INPUT);
  digitalWrite(IR_SENSOR_PIN, HIGH); // turns on the pullup resistor; this pin will read LOW when the beam is broken

  // Setup the other IR sensor
  pinMode(IR_SENSOR_PIN2, INPUT);
  digitalWrite(IR_SENSOR_PIN2, HIGH);

  // Setup v_pin
  pinMode(V_PIN, OUTPUT);
  digitalWrite(V_PIN, LOW);

  // setup interrupt so IR beam break calls function
  attachInterrupt(digitalPinToInterrupt(IR_SENSOR_PIN), beamBreak, FALLING);
  attachInterrupt(digitalPinToInterrupt(IR_SENSOR_PIN2), beamBreak, FALLING);

  // setup interrupt so we drop piece when the drop button is pressed
  attachInterrupt(digitalPinToInterrupt(DROP_PIECE_PIN), dropItem, RISING);

  // request to drop piece every 1.5 seconds
//  timer.every(1500, [](void*)->bool {dropItem(); return true;});
}

void loop() {
  timer.tick();
  closetimer.tick();
}
