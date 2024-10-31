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

class Sorter:

    def __init__(self) -> None:
        LEDpin = 18
        trayswitchpin = 16
        self.endpointUrl = "https://api.brickognize.com/predict/"

        self.pieceId0 = []
        self.pieceName0 = []
        self.pieceScore0 = []
        self.pieceId1 = []
        self.pieceName1 = []
        self.pieceScore1 = []
        self.pieceColor = []

        self.LED = GPIO.DigitalOutputDevice(LEDpin)

        self.traySwitch = GPIO.Button(trayswitchpin, bounce_time=0.05)

        

        #Initialize and configure Camera 0
        self.cam0 = Picamera2(0)
        camConfig0 = self.cam0.create_still_configuration(main={"size": (1024,768)}, lores={"size": (1024,768)}, display="lores")
        self.cam0.configure(camConfig0)
        self.cam0.start_preview(Preview.QTGL,x=1,y=1,width=320,height=200)
        self.cam0.start()

        #Initialize and configure Camera 1
        self.cam1 = Picamera2(1)
        camConfig1 = self.cam1.create_still_configuration(main={"size": (1024,768)}, lores={"size": (1024,768)}, display="lores")
        self.cam1.configure(camConfig1)
        self.cam1.start_preview(Preview.QTGL,x=1,y=260,width=320,height=200)
        self.cam1.start()

    def toggleLight(self):
        
        
        '''
        if lightState: 
            os.system("sudo uhubctl -l 1 -a 0 > /dev/null 2>&1")
            os.system("sudo uhubctl -l 3 -a 0 > /dev/null 2>&1")
        else:
            os.system("sudo uhubctl -l 1 -a 1 > /dev/null 2>&1")
            os.system("sudo uhubctl -l 3 -a 1 > /dev/null 2>&1")
        '''
        
        self.LED.toggle()
        
        return
    
    def camCap0(self, img0):
        
        res0 = requests.post(
            self.endpointUrl,
            headers={'accept': 'application/json'},
            files={'query_image': (img0, open(img0,'rb'), 'image/jpeg')},
        )
        
        data0 = json.loads(res0.content)
        
        for x in range(min(3, len(data0["items"]))):
            self.pieceId0.append(data0["items"][x]["id"])
            self.pieceName0.append(data0["items"][x]["name"])
            self.pieceScore0.append(data0["items"][x]["score"]*100)
            #print("  cam0: "+pieceId0[x]+" "+pieceName0[x]+": {:.2f}% confidence".format(pieceScore0[x]))
    
        start_x = int(data0["bounding_box"]["left"])
        end_x = int(data0["bounding_box"]["right"])
        start_y = int(data0["bounding_box"]["upper"])
        end_y = int(data0["bounding_box"]["lower"])
    
        originalImage = cv2.imread(img0)

        cropped_img = originalImage[start_y:end_y,start_x:end_x]

        cv2.imwrite(self.pieceName0[0]+".jpg" , cropped_img)
    
        img = Image.open(self.pieceName0[0]+".jpg")
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
                
        self.pieceColor.append(int(rTot/count))
        self.pieceColor.append(int(gTot/count))
        self.pieceColor.append(int(bTot/count))
    
        return
        
    def camCap1(self, img1):

        res1 = requests.post(
            self.endpointUrl,
            headers={'accept': 'application/json'},
            files={'query_image': (img1, open(img1,'rb'), 'image/jpeg')},
        )
        
        data1 = json.loads(res1.content)
    
        for x in range(min(3, len(data1["items"]))):
            self.pieceId1.append(data1["items"][x]["id"])
            self.pieceName1.append(data1["items"][x]["name"])
            self.pieceScore1.append(data1["items"][x]["score"]*100)
            #print("  cam1: "+pieceId1[x]+" "+pieceName1[x]+": {:.2f}% confidence".format(pieceScore1[x]))
    
        return


    def scanPart(self):
        
        self.pieceId0.clear()
        self.pieceId1.clear()
        self.pieceScore0.clear()
        self.pieceScore1.clear()
        self.pieceName0.clear()
        self.pieceName1.clear()
        self.pieceColor.clear()

        #start of the time benchmarking.
        starttime = time.time()

        img0 = "test0.jpg"
        img1 = "test1.jpg"

        self.cam0.capture_file(img0)
        self.cam1.capture_file(img1)

        print("Scanning...")
            
            
        self.camCap0(img0)
        self.camCap1(img1)
        
        print("\033[2J\033[H", end="", flush=True)
        print("Results:")

        for x in range(3):
            if x < len(self.pieceId0):
                print("  cam0: "+self.pieceId0[x]+" "+self.pieceName0[x]+": {:.2f}% confidence".format(self.pieceScore0[x]))
            if x < len(self.pieceId1):
                print("  cam1: "+self.pieceId1[x]+" "+self.pieceName1[x]+": {:.2f}% confidence".format(self.pieceScore1[x]))
        
        print(
            "R: {}\n".format(self.pieceColor[0]),
            "G: {}\n".format(self.pieceColor[1]),
            "B: {}\n".format(self.pieceColor[2])
        )
        
        
        endtime = time.time()
        
        #print("Imaging Time = {:.4f} seconds".format(picEnd-starttime))
        print("Process Time = {:.4f} seconds\n".format(endtime-starttime))
        
        return
    
    def close(self):
        self.cam0.close()
        self.cam1.close()

    def bindLightToggle(self):
        if not self.LED.value: self.LED.toggle()
        self.traySwitch.when_pressed = self.scanPart
 
if __name__ == "__main__":

    sorter = Sorter()
    sorter.bindLightToggle()
    
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
            sorter.close()
            exit()
        if userInput == "1": sorter.scanPart()
        if userInput == "2": sorter.toggleLight()
