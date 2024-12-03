#include <Servo.h>
#include <arduino-timer.h>

#include "SerialReader.h"
#include "Config.h"

// Define variables for the various servos and states
Servo flipper;
bool flipperLeft;

// bool to track if we're waiting to reactiveate the IR sensor
volatile bool bouncing = false;

// bool to track if we're waiting to reactivate the drop pin
volatile bool drop_bouncing = false;

// bool to track if vibration is on
volatile bool v_on = true;

// create timer to handle waiting while not blocking
auto timer = timer_create_default();
Timer<2, millis, byte> closetimer;

Servo gates[2];
const int8_t offsets[] = {LEFT_OFFSET, RIGHT_OFFSET};
const byte gate_pins[] = {LEFT_GATE_PIN, RIGHT_GATE_PIN};
bool hasItem[] = {false, false};

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
  if(hasItem[0] && hasItem[1]) {
    // Serial.println("Both bins occupied, dumping extra piece in current bin");
    return;
  }
  // One bin is free, assume it's the one we're currently dumping pieces into
  if (flipperLeft) {
    hasItem[0] = true;
    flipper.write(FLIPPER_RIGHT);
    // Serial.println("Left bin now has item");
  }
  else {
    hasItem[1] = true;
    timer.in(100, [](void*)->bool { flipper.write(FLIPPER_LEFT); return false;});
    // Serial.println("Right bin now has item");
  }
  flipperLeft = !flipperLeft;
  if (hasItem[0] && hasItem[1]) {
    // turn off vibration
    turnVibrationOff();
  }
}

void openGate(byte gateNum) {
  gates[gateNum].write(GATE_OPEN+offsets[gateNum]);
  hasItem[gateNum] = false;
  closetimer.in(500, closeGate, gateNum);
}

bool closeGate(byte gateNum) {
  gates[gateNum].write(GATE_CLOSE+offsets[gateNum]);
  return false;
}

// function called when the DROP_PIECE_PIN goes high
// or a timer calls it
void dropItem() {
  if (drop_bouncing) return;
  drop_bouncing = true;
  
  timer.in(500, [](void*) -> bool {drop_bouncing = false; return false;});
  // Serial.println("Dropping item...");

  // if both bins are occupied or neither bin is occupied, drop items out of the one where the flipper is pointing
  if ((hasItem[0] && hasItem[1]) || (!hasItem[0] && !hasItem[1])) {
    if (flipperLeft) { // flipper is pointing to the left, so open the left gate
      openGate(0);
    }
    else { // flipper is poing to the right, open the right gate
      openGate(1);
    }
  }
  // otherwise one bin has an item and we should open that bin
  else{
    if (hasItem[0]) {
      openGate(0);
//      Serial.println("Item dropped from left bin");
    }
    else {
      openGate(1);
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
    // Serial.println("Receiving item...");
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

  // Put the flipper servo and state into a starting configuration
  flipper.write(FLIPPER_LEFT);
  flipperLeft = true;

  for (byte i = 0; i < 2; i++) {
    gates[i].attach(gate_pins[i]);
    gates[i].write(GATE_CLOSE+offsets[i]);
  }

  // Setup the input pins for the drop button
  pinMode(DROP_PIECE_PIN, INPUT);

  // Setup the input pin for the IR sensor
  pinMode(IR_SENSOR_PIN, INPUT_PULLUP); //this pin will read LOW when the beam is broken

  // Setup v_pin
  pinMode(V_PIN, OUTPUT);
  digitalWrite(V_PIN, LOW);

  // setup interrupt so IR beam break calls function
  attachInterrupt(digitalPinToInterrupt(IR_SENSOR_PIN), beamBreak, FALLING);

  // setup interrupt so we drop piece when the drop button is pressed
  // attachInterrupt(digitalPinToInterrupt(DROP_PIECE_PIN), dropItem, RISING);

  // request to drop piece every 1.5 seconds
//  timer.every(1500, [](void*)->bool {dropItem(); return true;});
}

void loop() {
  timer.tick();
  closetimer.tick();
  
  // Process any characters received
  SerialReader.receiveData();
  // Checks if we've received a message over serial (any string ending in '\n'). If we have, check which code we got.
  if (SerialReader.hasMessage()) {
    char* message = SerialReader.getMessage();
    if (strcmp(message,"h") == 0) {
      if (hasItem[0] || hasItem[1]) {
        Serial.print("y\n");
      }
      else {
        Serial.print("n\n");
      }
    }
    else if (strcmp(message, "d") == 0) {
      dropItem();
    }
  }
}
