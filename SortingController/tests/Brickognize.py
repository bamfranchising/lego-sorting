import argparse
import cv2
import gpiozero
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

"""
pieceId0 = []
pieceName0 = []
pieceScore0 = []
pieceId1 = []
pieceName1 = []
pieceScore1 = []
"""

partID0 = ""
partName0 = ""
partScore0 = 0
partID1 = ""
partName1 = ""
partScore1 = 0


endpoint_url = "https://api.brickognize.com/predict/"
lightState = True
led = gpiozero.LED(17)

os.system("xdotool getactivewindow windowmove 100 100 windowsize --usehints 80 25")




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
    
    global lightState

    if lightState: 
        os.system("sudo uhubctl -l 1 -a 0 > /dev/null 2>&1")
        os.system("sudo uhubctl -l 3 -a 0 > /dev/null 2>&1")
    else:
        os.system("sudo uhubctl -l 1 -a 1 > /dev/null 2>&1")
        os.system("sudo uhubctl -l 3 -a 1 > /dev/null 2>&1")

    lightState = not lightState
    
    return
    
def camCap0(img0):
    
    global partID0
    global partName0
    global partScore0
    
    print("Starting camera 0...")
    
    res0 = requests.post(
        "https://api.brickognize.com/predict/",
        headers={'accept': 'application/json'},
        files={'query_image': (img0, open(img0,'rb'), 'image/jpeg')},
    )

    data0 = json.loads(res0.content)
    
    partID0 = data0["items"][1]["id"]
    partName0 = data0["items"][1]["name"]
    partScore0 = data0["items"][1]["score"]*100

    print(partID0)
    print("test!")
    
    """
    for x in range(3):
        pieceId0.append(data0["items"][x]["id"])
        pieceName0.append(data0["items"][x]["name"])
        pieceScore0.append(data0["items"][x]["score"]*100)
        print("  cam0: "+pieceId0[x]+" "+pieceName0[x]+": {:.2f}% confidence".format(pieceScore0[x]))
     """   
    print("Returning from camera 0!")
    
    return
    
def camCap1(img1):
    
    global partID1
    global partName1
    global partScore1
        
    print("Starting camera 1...")
    
    res1 = requests.post(
        "https://api.brickognize.com/predict/",
        headers={'accept': 'application/json'},
        files={'query_image': (img1, open(img1,'rb'), 'image/jpeg')},
    )

    data1 = json.loads(res1.content)
    partID1 = data1["items"][0]["id"]
    partName1 = data1["items"][0]["name"]
    partScore1 = data1["items"][0]["score"]*100
    
    
    """
    for x in range(3):
        pieceId1.append(data1["items"][x]["id"])
        pieceName1.append(data1["items"][x]["name"])
        pieceScore1.append(data1["items"][x]["score"]*100)
        print("  cam1: "+pieceId1[x]+" "+pieceName1[x]+": {:.2f}% confidence".format(pieceScore1[x]))
    """    
        
    
    print("Returning from camera 1!")
    
    return


def scanPart():
    
    global partID0
    global partName0
    global partScore0
    global partID1
    global partName1
    global partScore1

    #start of the time benchmarking.
    starttime = time.time()



    img0 = "test0.jpg"
    img1 = "test1.jpg"

    cam0.capture_file(img0)
    cam1.capture_file(img1)
    

    """
    # Write results to a .json file #
    with open('data.json', 'w') as f:
        #json.dump(data, f)
        f.write(
            json.dumps(data, indent=4)
        )
    """
    
    """
    start_x = int(data["bounding_box"]["left"])
    end_x = int(data["bounding_box"]["right"])
    start_y = int(data["bounding_box"]["upper"])
    end_y = int(data["bounding_box"]["lower"])
    """
    
    print("Results:")
    p0 = multiprocessing.Process(target=camCap0,args=(img0, ))
    p1 = multiprocessing.Process(target=camCap1,args=(img1, ))

    p0.start()
    p1.start()
    
    p0.join()
    p1.join()
        
    print("Returned!")
        
    """
    data = camCap0()
    data1 = camCap1()
    """
    
    #pieceId = [[0 for row in range(0,3)] for col in range(0,3)]
    #pieceName = [[0 for row in range(0,3)] for col in range(0,3)]
    #pieceScore = [[0 for row in range(0,3)] for col in range(0,3)]
    
    #pieceId0 = []
    #pieceName0 = []
    #pieceScore0 = []
    #pieceId1 = []
    #pieceName1 = []
    #pieceScore1 = []
    
    #for x in range(3):
    #    pieceId0.append(data0["items"][x]["id"])
    #    pieceName0.append(data0["items"][x]["name"])
    #    pieceScore0.append(data0["items"][x]["score"]*100)
    #    pieceId1.append(data1["items"][x]["id"])
    #    pieceName1.append(data1["items"][x]["name"])
    #    pieceScore1.append(data1["items"][x]["score"]*100)

    


    """
    originalImage = cv2.imread(img)

    cropped_img = originalImage[start_y:end_y,start_x:end_x]

    #rot_img = cv2.rotate(cropped_img, cv2.ROTATE_90_CLOCKWISE)

    cv2.imwrite(pieceName[0]+".jpg" , cropped_img)
    
    cv2.imshow(pieceName[0], cropped_img)
    cv2.waitKey(0)
    #cv2.imshow(pieceName[0], cropped_img)
    #cv2.waitKey(0)
    
    #img_rgb = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2RGB)
    #img_rgb = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2RGB)
    #cv2.imshow(pieceName[0],img_rgb)
    #cv2.waitKey(0)

    """
    
    
    print("\033[2J\033[H", end="", flush=True)
    print("Results:")
    print("  cam0: "+partID0+" "+partName0+": ") #{:.2f}% confidence".format(float(partScore0)))
    print("  cam1: "+partID1+" "+partName1+": ") #{:.2f}% confidence".format(float(partScore1)))
    
    
    
    """
    for x in range(2):
        print("  cam0: "+pieceId0[x]+" "+pieceName0[x]+": {:.2f}% confidence".format(num(pieceScore0[x]))
        print("  cam1: "+pieceId1[x]+" "+pieceName1[x]+": {:.2f}% confidence".format(pieceScore1[x]))
    """
    
    endtime = time.time()
    
    #print("Imaging Time = {:.4f} seconds".format(picEnd-starttime))
    print("Process Time = {:.4f} seconds\n".format(endtime-starttime))

    
    
    return



def main():

    # Initialize hardware:



    #toggleLight()
    
    
    
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
          
    return      
 
if __name__ == "__main__": main() 
