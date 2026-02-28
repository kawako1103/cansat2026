import serial
import time
import RPi.GPIO as GPIO
import datetime
import sys
import random
import os



ResetPin = 12
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(ResetPin,GPIO.OUT)
#GPIO.output(ResetPin,0)
device = '/dev/ttyS0'
ser = serial.Serial(device,115200,timeout = 1)
file_path = "/home/cansat-stu/Op-test_i2c/log_gps.txt"

def send(msg: str):
    ser.write(bytes(msg+'\r\n', encoding='utf-8'))
    time.sleep(0.1)

    while ser.in_waiting > 0:
        output = str(ser.readline(), encoding='utf-8', errors='replace')
        print(output, end='')
        if output == 'NG 103\r\n':
            print('no ACK')
        if output == 'NG 110\r\n':
            print('word over')


GPIO.output(ResetPin,1)
time.sleep(0.1)

GPIO.output(ResetPin,0)
time.sleep(2)

#send('1')#terminal>configration


def start_operation_mode():
    send("2")
    send("load")
    send("bw 6")
    send("panid 4321")
    send("ownid FFFE")
    send("ack 2")	
    send("rcvid 1")
    send("transmode 2")
    send("rssi 1")
    send("sf 7")
    send("save")
    send("start")
    
#def save_to_file(content, file_path):
#    with open(file_path, 'a') as file:
#        for line in content:
#            file.write(line + '\n')


def hex2dec(x: str, bit: int) -> str:
    dec = int(x, 16)
    if dec >> bit:
        raise ValueError
    return dec - (dec >> (bit - 1) << bit)

#def make_LatLon():
 #   vec_LatLon = []
 #   for _ in range(20):
 #       # Generate random latitude and longitude (64-bit)
 #       latitude = random.uniform(-90, 90)
 #       longitude = random.uniform(-180, 180)
 #       vec_LatLon.append((latitude, longitude))
 #       #print(latitude, longitude)
 #       time.sleep(0.05)  # Approx. 20 times per second
 #   return vec_LatLon
    
def read_LatLon(file_path, last_index):
    vec_LatLon=[]
    with open(file_path, "r") as file:
        lines=file.readlines()
        
        for i in range(last_index, len(lines)):
            line=lines[i]
            if '\xb3' in line:
                continue
            parts=line.strip().split(',')
            if len(parts) >= 2:
                latitude=parts[0]
                longitude=parts[1]
                vec_LatLon.append((latitude,longitude))
    return vec_LatLon, len(lines)



def send_LatLon(vec_LatLon):
    if not vec_LatLon:
       #output="0"*64+","+"0"*64+"\r\n"
      
        output="00000.00000"+","+"00000.00000"+"\r\n"
        ser.write(output.encode('ascii'))
        print(output.encode('ascii'))
        time.sleep(1)    
    
        
     #rint("No data to send.")
       
    for lat_lon in vec_LatLon:
        last_lat,last_lon=lat_lon
        
        #last_lat, last_lon = vec_LatLon[-1]
        output = f"{last_lat},{last_lon}\r\n"
        #output = f"4321FFFF{last_lat},{last_lon}\r\n"
        formatted_data = f"4321FFFF{last_lat},{last_lon}\r\n"
        #save_to_file([formatted_data], file_path)
        ser.write(output.encode('ascii'))
        print(output.encode('ascii'))
        time.sleep(1)    
    
    
    

# Test the functions
start_operation_mode()

#vec_LatLon=read_LatLon(file_path)
#send_LatLon(vec_LatLon)

last_index=0

while True:
    vec_LatLon,last_index=read_LatLon(file_path,last_index)
    send_LatLon(vec_LatLon)
    time.sleep(10)


#for _ in range(100):
   # vec_LatLon = make_LatLon()
   #send_LatLon(vec_LatLon)
   #time.sleep(1)
    


