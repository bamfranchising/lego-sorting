import argparse
import cv2
import gpiozero as GPIO
import json
import multiprocessing
import numpy as np
import os
import pandas as pd
from picamera2 import Picamera2, Preview
from PIL import Image
import requests
import subprocess
from sys import exit
import time


# define global variables:

pieceId0 = []
pieceName0 = []
pieceScore0 = []
pieceId1 = []
pieceName1 = []
pieceScore1 = []
pieceColor = []


LEDpin = 18
LED = GPIO.DigitalOutputDevice(LEDpin)


traySwitch = GPIO.Button(16, bounce_time=0.05)

endpointUrl = "https://api.brickognize.com/predict/"




'''
# Turn on USB ports:
os.system("sudo uhubctl -l 1 -a 1 > /dev/null 2>&1")
os.system("sudo uhubctl -l 3 -a 1 > /dev/null 2>&1")   
'''

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

def toggleLight():
    
    
    '''
    if lightState: 
        os.system("sudo uhubctl -l 1 -a 0 > /dev/null 2>&1")
        os.system("sudo uhubctl -l 3 -a 0 > /dev/null 2>&1")
    else:
        os.system("sudo uhubctl -l 1 -a 1 > /dev/null 2>&1")
        os.system("sudo uhubctl -l 3 -a 1 > /dev/null 2>&1")
    '''
    
    LED.toggle()
    
    return
    
def camCap0(img0):
    global endpointUrl
    global pieceId0
    global pieceName0
    global pieceScore0
    global pieceColor
    
    res0 = requests.post(
        endpointUrl,
        headers={'accept': 'application/json'},
        files={'query_image': (img0, open(img0,'rb'), 'image/jpeg')},
    )
    
    data0 = json.loads(res0.content)
    
    for x in range(3):
        pieceId0.append(data0["items"][x]["id"])
        pieceName0.append(data0["items"][x]["name"])
        pieceScore0.append(data0["items"][x]["score"]*100)
        #print("  cam0: "+pieceId0[x]+" "+pieceName0[x]+": {:.2f}% confidence".format(pieceScore0[x]))
 
    start_x = int(data0["bounding_box"]["left"])
    end_x = int(data0["bounding_box"]["right"])
    start_y = int(data0["bounding_box"]["upper"])
    end_y = int(data0["bounding_box"]["lower"])
 
    originalImage = cv2.imread(img0)

    cropped_img = originalImage[start_y:end_y,start_x:end_x]

    cv2.imwrite(pieceName0[0]+".jpg" , cropped_img)
 
    img = Image.open(pieceName0[0]+".jpg")
    img.convert('RGB')
    width, height = img.size
    
    rTot = 0
    gTot = 0
    bTot = 0
    count = 0
    
    for x in range(int(width*.4), int(width*.6)):
        for y in range(int(height*.4), int(height*.5)):
            r, g, b = img.getpixel((x,y))
            rTot += r
            gTot += g
            bTot += b
            count += 1
            
    pieceColor.append(int(rTot/count))
    pieceColor.append(int(gTot/count))
    pieceColor.append(int(bTot/count))
  
    return
    
def camCap1(img1):
    global endpointUrl
    global pieceId1
    global pieceName1
    global pieceScore1

    res1 = requests.post(
        endpointUrl,
        headers={'accept': 'application/json'},
        files={'query_image': (img1, open(img1,'rb'), 'image/jpeg')},
    )
    
    data1 = json.loads(res1.content)
   
    for x in range(3):
        pieceId1.append(data1["items"][x]["id"])
        pieceName1.append(data1["items"][x]["name"])
        pieceScore1.append(data1["items"][x]["score"]*100)
        #print("  cam1: "+pieceId1[x]+" "+pieceName1[x]+": {:.2f}% confidence".format(pieceScore1[x]))
 
    return


def scanPart():

    global pieceId0
    global pieceName0
    global pieceScore0
    global pieceId1
    global pieceName1
    global pieceScore1
    
    pieceId0.clear()
    pieceId1.clear()
    pieceScore0.clear()
    pieceScore1.clear()
    pieceName0.clear()
    pieceName1.clear()
    pieceColor.clear()

    #start of the time benchmarking.
    starttime = time.time()

    img0 = "test0.jpg"
    img1 = "test1.jpg"

    cam0.capture_file(img0)
    cam1.capture_file(img1)

    print("Scanning...")
         
        
    camCap0(img0)
    camCap1(img1)
    
    print("\033[2J\033[H", end="", flush=True)
    print("Results:")

    for x in range(3):
        print("  cam0: "+pieceId0[x]+" "+pieceName0[x]+": {:.2f}% confidence".format(pieceScore0[x]))
        print("  cam1: "+pieceId1[x]+" "+pieceName1[x]+": {:.2f}% confidence".format(pieceScore1[x]))
    
    print(
        "R: {}\n".format(pieceColor[0]),
        "G: {}\n".format(pieceColor[1]),
        "B: {}\n".format(pieceColor[2])
    )
    
    
    endtime = time.time()
    
    #print("Imaging Time = {:.4f} seconds".format(picEnd-starttime))
    print("Process Time = {:.4f} seconds\n".format(endtime-starttime))
    
    return
 
if __name__ == "__main__":
    
    if not LED.value: LED.toggle()
    
    
    traySwitch.when_pressed = scanPart
    
    
    
    # Clear console
    print("\033[2J\033[H", end="", flush=True)
    
    while True:

        print(
            "Select action:\n"
            "  0: Quit\n"
            "  1: Scan part\n"
            "  2: Toggle light\n"
        )
        userInput = input(">>> ")
        if userInput == "0": 
            
            cam0.close()
            #cam0.stop_preview(Preview.QTGL)
            
            cam1.close()
            #cam1.stop_preview(Preview.QTGL)
            exit()
        if userInput == "1": scanPart()
        if userInput == "2": toggleLight()
