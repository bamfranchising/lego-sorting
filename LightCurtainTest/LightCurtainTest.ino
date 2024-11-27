

#define SENSOR_PIN 2

void beamBreak() {
    static unsigned int brick_count = 0;
    Serial.print("Brick Detected! #");
    Serial.println(brick_count++);
}

void setup() {
    Serial.begin(115200);
    pinMode(SENSOR_PIN, INPUT_PULLUP);

    attachInterrupt(digitalPinToInterrupt(SENSOR_PIN), beamBreak, FALLING);
}

void loop() {
}

