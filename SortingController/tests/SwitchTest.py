
#!/usr/bin/env python3

import signal
import sys
import gpiozero as GPIO


btn = GPIO.Button(16, bounce_time=0.01)



def signal_handler(sig, frame):
    sys.exit(0)

def btnPressed():
    print("The button was pressed!")
    return

def btnReleased():
    print("The button was released!")
    return

if __name__ == '__main__':
    
    btn.when_pressed = btnPressed
    btn.when_released = btnReleased
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()
