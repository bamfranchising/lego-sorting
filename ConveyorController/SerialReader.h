class SR {
private:
  bool newData = false; // flag for whether entire message has been received.
  byte ndx = 0;         // index into which we should put data
  char endMarker = '\n';// character indicating end of message
  static const byte numChars = 3; // size of char array to hold incoming serial data
  char receivedChars[numChars];   // an array to store the received serial data
public:

  SR(char ec = '\n') : endMarker(ec) {}

  // Function to change the endline character from default
  void setEndlineCharacter(char ec) { endMarker = ec; }

  // Checks if entire message has been received
  bool hasMessage() { return newData; }

  // Returns pointer to the char array containing the message
  char* getMessage() { newData = false; return receivedChars; }

  // Reads data from Serial if there is any
  void receiveData() {
    char rc;
    while (Serial.available() > 0 && newData == false) { // while there is data available and we haven't hit end of message
      rc = Serial.read();  // read the next char.
      
      if (rc != endMarker) {     // if it's not the end of the message
        receivedChars[ndx] = rc; // tack it onto the message at ndx
        ndx++;                   // increment ndx.
        if (ndx >= numChars) {   // if we try to write past the allotted memory
          ndx = numChars - 1;     // push ndx back to end of allotted memory
        }
      }
      else { // if it is the end of the message
        receivedChars[ndx] = '\0'; // terminate the string
        ndx = 0;                   // reset ndx to beginning of memory
        newData = true;            // set the flag that we have the whole message
      }
    }
  }
};

SR SerialReader; // Setup global instance of SerialReader