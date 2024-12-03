import serial
import cv2
# import gpiozero as GPIO
import json
from picamera2 import Picamera2, Preview
from PIL import Image#, ImageTk
import requests
from sys import exit
import time
import tkinter
from copy import deepcopy

class Sorter:
    def __init__(self) -> None:
        pass

    #Function to determine where a given piece should be placed.
    #Data is assumed to be an object of the form of the JSON response
    #from Brickognize: https://api.brickognize.com/docs#/predict/predict_predict__post
    def place_piece(self, data)->int:

        category = ""
        if len(data["items"]) > 0:
            category = data["items"][0]["category"]
        else:
            return -1
        # potential categories: Brick, Plate, Bracket, Minifigure, Technic, Wheel
        # For the 5 sections we have now, we divide into Bricks, Plates (including brackets), Minifigure, Technic and Wheels, and Other
        if "Brick" in category:
            return 0
        elif "Plate" in category or "Bracket" in category:
            return 1
        elif "Minifigure" in category or "Technic" in category or "Wheels" in category:
            return 2
        else:
            return -1

class SorterDriver:

    def __init__(self) -> None:

        self.servo_queue = [[0,0,0,0,0],
                            [0,0,0,0,0,0],
                            [0,0,0,0,0,0,0],
                            [0,0,0,0,0,0,0,0]]
        
        self.DELAY_BETWEEN_DISPENSE_AND_SCAN = 500
        self.DELAY_BETWEEN_DROP_AND_DISPENSE = 1000
        
        stager_com_port = "/dev/ttyACM0"
        conveyor_com_port = "/dev/ttyUSB0"

        self.stager_serial = serial.Serial(stager_com_port, 115200, timeout=3)
        self.conveyor_serial = serial.Serial(conveyor_com_port, 115200)

        self.scanning = False

        self.sorter = Sorter()

        self.app = tkinter.Tk()
        self.app.title("LEGO Sorting Machine")
        self.app.geometry('640x600')
        self.app.bind('<Escape>', lambda e: self.app.quit())

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
        
        self.endpointUrl = "https://api.brickognize.com/predict/"

        self.pieceId0 = []
        self.pieceName0 = []
        self.pieceScore0 = []
        self.pieceId1 = []
        self.pieceName1 = []
        self.pieceScore1 = []
        self.pieceColor = []

        StartScanningButton = tkinter.Button(self.app,
            text = "Start Scanning",
            command = self.startScanning,
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
        StopScanningButton = tkinter.Button(self.app,
            text = "Stop Scanning",
            command = self.stopScanning,
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

        # LED_button = tkinter.Button(self.app,
        #     text = "Toggle Light",
        #     command = self.toggleLight,
        #     activebackground = "blue",
        #     activeforeground = "white",
        #     anchor = "center",
        #     bd = 3,
        #     bg = "lightgray",
        #     cursor = "hand2",
        #     disabledforeground = "gray",
        #     fg = "black",
        #     font = ("Arial", 12),
        #     height = 2,
        #     highlightbackground = "black",
        #     highlightcolor = "green",
        #     highlightthickness = 2,
        #     justify = "center",
        #     overrelief = "raised",
        #     padx = 10,
        #     pady = 5,
        #     width = 15,
        #     wraplength = 100)
            
        #CAMERA_button.pack(padx = 20, pady = 20)
        # LED_button.pack(padx = 2, pady = 10)
        StartScanningButton.pack(padx = 2, pady = 10)
        StopScanningButton.pack(padx = 2, pady = 10)

        

    # def toggleLight(self):
        
        
    #     '''
    #     if lightState: 
    #         os.system("sudo uhubctl -l 1 -a 0 > /dev/null 2>&1")
    #         os.system("sudo uhubctl -l 3 -a 0 > /dev/null 2>&1")
    #     else:
    #         os.system("sudo uhubctl -l 1 -a 1 > /dev/null 2>&1")
    #         os.system("sudo uhubctl -l 3 -a 1 > /dev/null 2>&1")
    #     '''
        
    #     self.LED.toggle()
        
    #     return

    def startScanning(self):
        if not self.scanning:
            self.scanning = True
            self.app.after(self.DELAY_BETWEEN_DISPENSE_AND_SCAN, sorter.scanPart)

    def stopScanning(self):
        self.scanning = False
    
    def getPrediction(self, img):
        res0 = requests.post(
            self.endpointUrl,
            headers={'accept': 'application/json'},
            files={'query_image': (img, open(img,'rb'), 'image/jpeg')},
        )
        # print(res0.content)
        data = json.loads(res0.content)
        return data
    
    def getPieceColor(self, data0, img0):
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

    # function to combine the probabilities from each of the data sets. Returns the combined probabilities
    def combine_probabilities(self, data0, data1):
        # deep copy the items from data0 as the basis for the combined data
        data = deepcopy(data0)
        # perform a 50/50 weighted average of the score of the items

        # go through the data0 collection and keep track of the IDs we encounter and their positions in the list
        ids_in_data = set()
        index = {}
        for i in range(len(data["items"])):
            # weight the score
            data["items"][i]["score"] *= 0.5
            # add the id to the set of IDs we've seen
            ids_in_data.add(data["items"][i]["id"])
            # add the (id, index) pair to a dictionary for later use
            index[data["items"][i]["id"]] = i
        
        # iterate through the second list of items
        for i in range(len(data1["items"])):
            id = data1["items"][i]["id"]
            # weight the score of the item
            data1["items"][i]["score"] *= 0.5
            # if we've seen the id before
            if id in ids_in_data:
                # add our weighted score to the other one
                data["items"][index[id]]["score"] += data1["items"][i]["score"]
            else:
                # haven't seen it, so add it to the list (with the weighted score)
                data["items"].append(data1["items"][i])

        # sort the list of items by their combined score
        data["items"].sort(key=lambda x: x["score"], reverse=True)
        return data

    def partToBin(self, binNum):
        message = str(binNum) + "\n"
        self.conveyor_serial.write(message.encode())
    
    def tryDispensePart(self):
        self.stager_serial.write(b'h\n')
        read = self.stager_serial.readline()
        readstr = read.decode("utf-8")
        
        if (readstr == "y\n"):
            self.stager_serial.write(b'd\n')
            return True
        else:
            return False

    def scanPart(self):
        while not self.tryDispensePart():
            time.sleep(.5)
            if not self.scanning: return
        
        time.sleep(self.DELAY_BETWEEN_DISPENSE_AND_SCAN/1000)
        
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
        
        data0 = self.getPrediction(img0)
        data1 = self.getPrediction(img1)
        
        print("\033[2J\033[H", end="", flush=True)
        print("Results:")

        for x in range(max(len(data0["items"]), len(data1["items"]))):
            if x < len(data0["items"]):
                print("  cam0: "+data0["items"][x]["id"]+" "+data0["items"][x]["name"]+": {:.2f}% confidence".format(data0["items"][x]["score"]*100) + " " + data0["items"][x]["category"])
            if x < len(data1["items"]):
                print("  cam1: "+data1["items"][x]["id"]+" "+data1["items"][x]["name"]+": {:.2f}% confidence".format(data1["items"][x]["score"]*100) + " " + data1["items"][x]["category"])
            #print("  cam1: "+pieceId1[x]+" "+pieceName1[x]+": {:.2f}% confidence".format(pieceScore1[x]))

        data = self.combine_probabilities(data0, data1)
        print("Combined Results:")
        for i in range(len(data["items"])):
            print("  "+data["items"][i]["id"]+" "+data["items"][i]["name"]+": {:.2f}% confidence".format(data["items"][i]["score"]*100) + " " + data["items"][i]["category"])
        # self.getPieceColor(data0, img0)
        
        # if len(self.pieceColor) == 3:
        #     print(
        #         "R: {}\n".format(self.pieceColor[0]),
        #         "G: {}\n".format(self.pieceColor[1]),
        #         "B: {}\n".format(self.pieceColor[2])
        #     )
        
        bin_num = self.sorter.place_piece(data)
        print("Item to go in bin number " + str(bin_num))
        self.partToBin(bin_num)
        endtime = time.time()
        
        #print("Imaging Time = {:.4f} seconds".format(picEnd-starttime))
        print("Process Time = {:.4f} seconds\n".format(endtime-starttime))

        if self.scanning:
            self.app.after(self.DELAY_BETWEEN_DROP_AND_DISPENSE, self.scanPart)

    def destroy(self): 
        self.cam0.close()
        self.cam1.close()
        self.stager_serial.close()
        self.conveyor_serial.close()

    # def toggleLight(self):
    #     self.LED.toggle() 
    #     if self.LED.value: 
    #         print("Turn on LED ...") 
    #     else: 
    #         print("Turn off LED ... ")



if __name__ == '__main__': # Program entrance
    sorter = SorterDriver()
    sorter.app.mainloop()
    
    sorter.destroy()
    exit()
