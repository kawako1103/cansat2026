import RPi.GPIO as GPIO
import time

# GPIO
GPIO.setmode(GPIO.BCM)

#
# GPIO.setup(21, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(26, GPIO.OUT, initial=GPIO.LOW)


def cutWire():
    ##
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    # GPIO.setup(21, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(26, GPIO.OUT, initial=GPIO.LOW)
    ##

    try:
        i = 0
        while i < 3:

            # GPIO.output(21, GPIO.HIGH)
            GPIO.output(26, GPIO.LOW)
            time.sleep(1.5)

            # GPIO.output(21, GPIO.LOW)
            GPIO.output(26, GPIO.HIGH)
            time.sleep(1.5)
            i += 1
    except KeyboardInterrupt:
        # GPIO.cleanup()
        # GPIO.cleanup(21)
        GPIO.cleanup(26)

    finally:
        # GPIO.cleanup()
        # GPIO.cleanup(21)
        GPIO.cleanup(26)


if __name__ == "__main__":
    cutWire()
