from adafruit_servokit import ServoKit
import argparse
import cv2
import gpiozero as GPIO
import json
import multiprocessing
import numpy as np
import os
import pandas as pd
from picamera2 import Picamera2, Preview
from PIL import Image, ImageTk
import requests
import subprocess
from sys import exit
import time
import tkinter

app = tkinter.Tk()
app.title("LEGO Sorting Machine")
app.geometry('640x600')
app.bind('<Escape>', lambda e: app.quit())


#Initialize servo hat
kit = ServoKit(channels=16)
kit.servo[3].angle = 0
kit.servo[2].angle = 0
kit.servo[1].angle = 0
kit.servo[0].angle = 0

''' OLD CODE FOR RUNNING SERVOS DIRECTLY FROM GPIO
gpio_A = 6
gpio_B = 13
gpio_C = 19
gpio_D = 26
 
servo_A = GPIO.Servo(gpio_A)
servo_B = GPIO.Servo(gpio_B)
servo_C = GPIO.Servo(gpio_C)
servo_D = GPIO.Servo(gpio_D)

servo_A.min()
servo_B.min()
servo_C.min()
servo_D.min()
'''

DROP_PIN = 5
DROPPER = GPIO.DigitalOutputDevice(DROP_PIN)

LED_pin = 18
LED = GPIO.DigitalOutputDevice(LED_pin)

MOTOR_pin = 21                                       
MOTOR = GPIO.DigitalOutputDevice(MOTOR_pin)

#Initialize and configure Camera 0
cam0 = Picamera2(0)
camConfig0 = cam0.create_still_configuration(main={"size": (1024,768)}, lores={"size": (1024,768)}, display="lores")
cam0.configure(camConfig0)
cam0.start_preview(Preview.QTGL,x=1,y=1,width=320,height=200)
cam0.start()

#Initialize and configure Camera 1
cam1 = Picamera2(1)
camConfig1 = cam1.create_still_configuration(main={"size": (1024,768)}, lores={"size": (1024,768)}, display="lores")
cam1.configure(camConfig1)
cam1.start_preview(Preview.QTGL,x=1,y=260,width=320,height=200)
cam1.start()


def dropTest():
    DROPPER.toggle()
    if DROPPER.value:
        print("Signal high")
    else:
        print("Signal low")

def destroy(): 
    LED.close() 
    MOTOR.close()
    DROPPER.close()
    exit()

def toggleLight():
    LED.toggle() 
    if LED.value: 
        print("Turn on LED ...") 
    else: 
        print("Turn off LED ... ")

def toggleMotor():
    MOTOR.toggle()
    if MOTOR.value: 
        print("Turn on Motor ...") 
    else: 
        print("Turn off Motor ... ")

def toggleServo(servo_num):
    kit.servo[servo_num].angle = 120
    time.sleep(1)
    kit.servo[servo_num].angle = 0

LED_button = tkinter.Button(app,
    text = "Toggle Light",
    command = toggleLight,
    activebackground = "blue",
    activeforeground = "white",
    anchor = "center",
    bd = 3,
    bg = "lightgray",
    cursor = "hand2",
    disabledforeground = "gray",
    fg = "black",
    font = ("Arial", 12),
    height = 2,
    highlightbackground = "black",
    highlightcolor = "green",
    highlightthickness = 2,
    justify = "center",
    overrelief = "raised",
    padx = 10,
    pady = 5,
    width = 15,
    wraplength = 100)

MOTOR_button = tkinter.Button(app,
    text = "Toggle Motor",
    command = toggleMotor,
    activebackground = "blue",
    activeforeground = "white",
    anchor = "center",
    bd = 3,
    bg = "lightgray",
    cursor = "hand2",
    disabledforeground = "gray",
    fg = "black",
    font = ("Arial", 12),
    height = 2,
    highlightbackground = "black",
    highlightcolor = "green",
    highlightthickness = 2,
    justify = "center",
    overrelief = "raised",
    padx = 10,
    pady = 5,
    width = 15,
    wraplength = 100)

Servo_A_button = tkinter.Button(app,
    text = "Servo A",
    command = lambda: toggleServo(0),
    activebackground = "blue",
    activeforeground = "white",
    anchor = "center",
    bd = 3,
    bg = "lightgray",
    cursor = "hand2",
    disabledforeground = "gray",
    fg = "black",
    font = ("Arial", 12),
    height = 2,
    highlightbackground = "black",
    highlightcolor = "green",
    highlightthickness = 2,
    justify = "center",
    overrelief = "raised",
    padx = 10,
    pady = 5,
    width = 15,
    wraplength = 100)

Servo_B_button = tkinter.Button(app,
    text = "Servo B",
    command = lambda: toggleServo(1),
    activebackground = "blue",
    activeforeground = "white",
    anchor = "center",
    bd = 3,
    bg = "lightgray",
    cursor = "hand2",
    disabledforeground = "gray",
    fg = "black",
    font = ("Arial", 12),
    height = 2,
    highlightbackground = "black",
    highlightcolor = "green",
    highlightthickness = 2,
    justify = "center",
    overrelief = "raised",
    padx = 10,
    pady = 5,
    width = 15,
    wraplength = 100)

Servo_C_button = tkinter.Button(app,
    text = "Servo C",
    command = lambda: toggleServo(2),
    activebackground = "blue",
    activeforeground = "white",
    anchor = "center",
    bd = 3,
    bg = "lightgray",
    cursor = "hand2",
    disabledforeground = "gray",
    fg = "black",
    font = ("Arial", 12),
    height = 2,
    highlightbackground = "black",
    highlightcolor = "green",
    highlightthickness = 2,
    justify = "center",
    overrelief = "raised",
    padx = 10,
    pady = 5,
    width = 15,
    wraplength = 100)
    
Servo_D_button = tkinter.Button(app,
    text = "Servo D",
    command = lambda: toggleServo(3),
    activebackground = "blue",
    activeforeground = "white",
    anchor = "center",
    bd = 3,
    bg = "lightgray",
    cursor = "hand2",
    disabledforeground = "gray",
    fg = "black",
    font = ("Arial", 12),
    height = 2,
    highlightbackground = "black",
    highlightcolor = "green",
    highlightthickness = 2,
    justify = "center",
    overrelief = "raised",
    padx = 10,
    pady = 5,
    width = 15,
    wraplength = 100)   

DROPPER_button = tkinter.Button(app,
    text = "Toggle Dropper",
    command = dropTest,
    activebackground = "blue",
    activeforeground = "white",
    anchor = "center",
    bd = 3,
    bg = "lightgray",
    cursor = "hand2",
    disabledforeground = "gray",
    fg = "black",
    font = ("Arial", 12),
    height = 2,
    highlightbackground = "black",
    highlightcolor = "green",
    highlightthickness = 2,
    justify = "center",
    overrelief = "raised",
    padx = 10,
    pady = 5,
    width = 15,
    wraplength = 100)
    
#CAMERA_button.pack(padx = 20, pady = 20)
LED_button.pack(padx = 2, pady = 10)
MOTOR_button.pack(padx = 2, pady = 10)
Servo_A_button.pack(padx = 2, pady = 10)
Servo_B_button.pack(padx = 2, pady = 10)
Servo_C_button.pack(padx = 2, pady = 10)
Servo_D_button.pack(padx = 2, pady = 10)
DROPPER_button.pack(padx = 2, pady = 10)



if __name__ == '__main__': # Program entrance

    app.mainloop()
    
    destroy()
