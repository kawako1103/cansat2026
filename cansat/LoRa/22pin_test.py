import RPi.GPIO as GPIO
import time

RESET_PIN = 22

# GPIO config
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
#GPIO.setmode(GPIO.BCM)
GPIO.setup(RESET_PIN, GPIO.OUT)  

try:
    while True:
        GPIO.output(RESET_PIN, 1)
        time.sleep(3)
        GPIO.output(RESET_PIN, 0)
        time.sleep(3)
        #GPIO.output(RESET_PIN, GPIO.HIGH)  
        #time.sleep(2)  
        #GPIO.output(RESET_PIN, GPIO.LOW)  
        #time.sleep(2)  
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup() 
