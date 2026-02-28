import serial
import time
import RPi.GPIO as GPIO
import datetime
import sys

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

send('1')

def start_operation_mode():
    send('z')
    while True:
        while ser.in_waiting > 0:
            out_str = str(ser.readline(), encoding='utf-8', errors='replace')
            RSSI_hex, PAN, ID, DATA = out_str[:4], out_str[4:8], out_str[8:12], out_str[12:]
            print(f"{hex2dec(RSSI_hex, 16)}dBm")
            # print(out_str)


def hex2dec(x: str, bit: int) -> str:
    dec = int(x, 16)
    if dec >> bit:
        raise ValueError
    return dec - (dec >> (bit - 1) << bit)
