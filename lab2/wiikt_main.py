#!/usr/bin/env python

#######################################################################
#                            Aufgabe 2                                #
#######################################################################

import threading
import signal
import sys
import math

from linuxWiimoteLib import *

running = True

class Wii_Control(threading.Thread):
    def __init__(self, freq = 10):
        threading.Thread.__init__(self)
        # set polling frequency
        self.freq = freq
        # initialize wiimote
        self.wiimote = Wiimote()
        # Insert address and name of device here
        device = ('8C:CD:E8:B4:41:07', 'Nintendo RVL-CNT-01-TR')
        connected = False

        try:
            print("Press any key on wiimote to connect")
            while (not connected):
                connected = self.wiimote.Connect(device)

            print("succesfully connected")

        except KeyboardInterrupt:
            print("Exiting through keyboard event (CTRL + C)")
            self.stop()
            exit(self.wiimote)

    def run(self):
        global running
        self.wiimote.SetAccelerometerMode()
        print("run method")
        wiistate = self.wiimote.WiimoteState
        while running:
            # re-calibrate accelerometer
            if (wiistate.ButtonState.Home):
                print("re-calibrating")
                self.wiimote.calibrateAccelerometer()
                sleep(1/self.freq)
        exit(self.wiimote)

def stop():
    global running
    running = False

def signal_handler(sig, frame):
    global running
    running = False

if __name__ == "__main__":
    wii_control = Wii_Control()
    # initialize sigint handler
    signal.signal(signal.SIGINT, signal_handler)
    wii_control.start()
    signal.pause()
    wii_control.join()
