from gpiozero import Servo
from time import sleep
 
gpio_A = 6
gpio_B = 13
gpio_C = 19
gpio_D = 26
 
servo_A = Servo(gpio_A)
servo_B = Servo(gpio_B)
servo_C = Servo(gpio_C)
servo_D = Servo(gpio_D)

 
while True:
    print(
        "1 - Extend A\n"
        "2 - Extend B\n"
        "3 - Extend C\n"
        "4 = Extend D\n"
        "5 - Retract all\n"
        "0 - Quit"
    )
    userInput = input(">>>")
    
    if userInput == "0":
        servo_A.min()
        servo_B.min()
        servo_C.min()
        servo_D.min()
        sleep(1)
        
        exit()
    
    if userInput == "1":
        servo_A.max()

    if userInput == "2":
        servo_B.max()

    if userInput == "3":
        servo_C.max()

    if userInput == "4":
        servo_D.max()
    
    if userInput == "5":
        servo_A.min()
        servo_B.min()
        servo_C.min()
        servo_D.min()

