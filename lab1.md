# 1.e)
Erstellen Sie ein Bashskript welches die beiden LEDs abwechselnd für eine Sekunde aufleuchten lässt.
```bash
#!/bin/bash

while true
do
    # red LED / port 17
    echo "1" > /sys/class/gpio/gpio17/value
    sleep "1"
    echo "0" > /sys/class/gpio/gpio17/value
    # green LED / port 18
    echo "1" > /sys/class/gpio/gpio18/value
    sleep "1"
    echo "0" > /sys/class/gpio/gpio18/value
done
```

# 1.f)
Erstellen Sie ein weiteres Bashskript, welches periodisch den Zustand des angeschlossenen Tasters ausgibt.
```bash
#!/bin/bash

while true
do
    # button / port 2
    cat /sys/class/gpio/gpio2/value
    sleep "1"
done
```


# 2.a)
Implementieren Sie eine while Schleife, welche die zwei LEDs abwechselnd für eine Sekunde aufleuchten lässt. Nutzen Sie dazu das Python Modul RPi.GPIO.
```python
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
```

# 2.b)
Erstellen Sie nun eine Thread Klasse LED, die eine LED (an einem bestimmten Pin) mit einer vorgegebenen Frequenz blinken lässt.
```python
import time
import threading

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
```

# 2.c)
Schreiben Sie ein Skript, welches zwei LED Threads startet. Beim Drücken des Tasters soll die Frequenz auf einen neuen, zufällig gewählten Wert gesetzt werden.
```python
# Add this to the code from 2.b)

import random

# seed random number generator
random.seed()

# start 2 LED threads
t1 = LED(17)
t2 = LED(18)

GPIO.setup(2, GPIO.IN)

try:
    while 1:
        # wait for input
        if GPIO.input(2):
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
        time.sleep(0.05)
except:
    pass
finally:
    GPIO.cleanup()
    t1.terminate()
    t2.terminate()
    t1.join()
    t2.join()
```
