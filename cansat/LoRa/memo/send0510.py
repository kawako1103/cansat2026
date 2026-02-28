import serial
import time
import RPi.GPIO as GPIO
import datetime
import sys
import random



ResetPin = 12
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(ResetPin,GPIO.OUT)
#GPIO.output(ResetPin,0)
device = '/dev/ttyS0'
ser = serial.Serial(device,115200,timeout = 1)

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
    


def hex2dec(x: str, bit: int) -> str:
    dec = int(x, 16)
    if dec >> bit:
        raise ValueError
    return dec - (dec >> (bit - 1) << bit)

def make_LatLon():
    vec_LatLon = []
    for _ in range(20):
        # Generate random latitude and longitude (64-bit)
        latitude = random.uniform(-90, 90)
        longitude = random.uniform(-180, 180)
        vec_LatLon.append((latitude, longitude))
        #print(latitude, longitude)
        time.sleep(0.05)  # Approx. 20 times per second
    return vec_LatLon


def send_LatLon(vec_LatLon):
    if not vec_LatLon:
        print("No data to send.")
        return
    last_lat, last_lon = vec_LatLon[-1]
    #output = f"{last_lat},{last_lon}\r\n"
    output = f"4321FFFF{last_lat},{last_lon}\r\n"
    
    ser.write(output.encode('ascii'))
    print(output.encode('ascii'))
    
    
    
    

# Test the functions
start_operation_mode()

for _ in range(100):
    vec_LatLon = make_LatLon()
    send_LatLon(vec_LatLon)



