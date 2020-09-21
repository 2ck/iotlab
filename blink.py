import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)

try:
    while 1:
        # red LED
        GPIO.output(17, 1)
        time.sleep(1)
        GPIO.output(17, 0)
        # green LED
        GPIO.output(18, 1)
        time.sleep(1)
        GPIO.output(18, 0)
except:
    pass
finally:
    GPIO.cleanup()
