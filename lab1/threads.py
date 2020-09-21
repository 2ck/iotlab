import time
import threading
import random

random.seed()

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

class LED(threading.Thread):
    def __init__(self, pin, freq = 1): # 1Hz default frequency
        threading.Thread.__init__(self)

        self.pin = pin
        self.freq = freq
        self.running = True
        GPIO.setup(self.pin, GPIO.OUT)
    def run(self):
        while self.running:
            GPIO.output(self.pin, 1)
            time.sleep(1/self.freq)
            GPIO.output(self.pin, 0)
            time.sleep(1/self.freq)
    def terminate(self):
        self.running = False

# start 2 LED threads
t1 = LED(17)
t2 = LED(18)
t1.start()
t2.start()

GPIO.setup(2, GPIO.IN)

try:
    while 1:
        # wait for input
        if not GPIO.input(2):
            # generate new random frequencies between
            # lower and upper bound and round to two
            # decimal places
            lb = 0.5
            ub = 10
            rf1 = round(random.uniform(lb, ub), 2)
            rf2 = round(random.uniform(lb, ub), 2)
            # terminate old threads
            t1.terminate()
            t2.terminate()
            t1.join()
            t2.join()
            # start new threads
            t1 = LED(17, rf1)
            t2 = LED(18, rf2)
            t1.start()
            t2.start()
        time.sleep(0.05)
except:
    pass
finally:
    GPIO.cleanup()
    t1.terminate()
    t2.terminate()
    t1.join()
    t2.join()
