#!/usr/bin/env python

from gpiozero import DigitalOutputDevice, Button
import tkinter as tk

root = tk.Tk()
root.title("LEGO Sorting Machine")
root.geometry('640x400')

LEDpin = 18 # define the relayPin 

LED = DigitalOutputDevice(LEDpin) # define LED pin according to BCM Numbering

MOTORpin = 21

MOTOR = DigitalOutputDevice(MOTORpin)


def toggleLight(): # When button is pressed, this function will be executed 
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


def destroy(): 
    LED.close() 
    MOTOR.close()
    exit()

LED_button = tk.Button(root,
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
    font = ("Arial", 16),
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
    
MOTOR_button = tk.Button(root,
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
    font = ("Arial", 16),
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
    
LED_button.pack(padx = 20, pady = 20)
MOTOR_button.pack(padx = 20, pady = 20)

if __name__ == '__main__': # Program entrance
    
    root.mainloop()
    
    destroy()
    
    """
    print("\033[2J\033[H", end="", flush=True)
    
    while True:

        print(
            "Select action:\n"\
            "  0: Quit\n"
            "  1: Scan part\n"
            "  2: Toggle light\n"
        )    
    
        userInput = input(">>> ")
        if userInput == "0": 
            destroy()
    
        if userInput == "2": toggleLight()
    """
