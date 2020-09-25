#!/usr/bin/python
import os
from time import time, sleep
import threading
import RPi.GPIO as GPIO
import smbus
import math

GPIO.setmode(GPIO.BCM)

# 1 indicates /dev/i2c-1 (port I2C1)
bus = smbus.SMBus(1)


POLLING_FREQ = 50 # Hz

#################################################################################
# Sensors
#################################################################################

#################################################################################
# Ultrasonic
#################################################################################

class Ultrasonic():
    '''This class is responsible for handling i2c requests to an ultrasonic sensor'''

    def __init__(self,address):
        print("init ultrasonic with addr", address)
        self.address = address
    
    # Aufgabe 2
    #
    # Diese Methode soll ein Datenbyte an den Ultraschallsensor senden um eine Messung zu starten
    def write(self,value):
        global bus
        try:
            bus.write_byte_data(self.address, 0x00, value)
        except Exception as e:
            #print("Ultrasonic write exception", e)
            pass

    # Aufgabe 2
    #
    # Diese Methode soll den Lichtwert auslesen und zurueckgeben.
    def get_brightness(self):
        global bus
        try:
            return bus.read_byte_data(self.address, 0x01)
        except Exception as e:
            #print("Brightness read exception", e)
            return -1

    # Aufgabe 2
    #
    # Diese Methode soll die Entfernung auslesen und zurueckgeben. 
    def get_distance(self):
        global bus
        # measure in cm
        self.write(0x51)
        # measurement takes 65ms max
        sleep(0.07)
        readsucc = True
        try:
            hi_b = bus.read_byte_data(self.address, 0x02)
            #print("ultrasonic hi read success", hi_b)
        except Exception as e:
            #print("Ultrasonic hi read exception", e)
            #hi_b = 0
            readsucc = False
        try:
            lo_b = bus.read_byte_data(self.address, 0x03)
            #print("ultrasonic lo read success", lo_b)
        except Exception as e:
            pass
            #print("Ultrasonic lo read exception", e)
            #lo_b = 0
            readsucc = False
        #return int.from_bytes(bytes([hi_b, lo_b]), byteorder="big")
        if readsucc:
            return ((hi_b << 8) + lo_b)
        else:
            return -1

    def get_address(self):
        return self.address

class UltrasonicThread(threading.Thread):
    ''' Thread-class for holding ultrasonic data '''

    # distance to obstacle in cm
    distance = 0

    # brightness value
    brightness = 0

    # Aufgabe 4
    #
    # Hier muss der Thread initialisiert werden.
    def __init__(self, address):
        threading.Thread.__init__(self)

        self.stopped = False

        self.ultrasonic = Ultrasonic(address)
        self.setDaemon(True)
        self.start()

    # Aufgabe 4
    #
    # Schreiben Sie die Messwerte in die lokalen Variablen
    def run(self):
        while not self.stopped:
            dist = self.ultrasonic.get_distance()
            if (dist >= 10):
                self.distance = dist
            bright = self.ultrasonic.get_brightness()
            if (bright >= 0):
                self.brightness = bright
            
    def stop(self):
        self.stopped = True

#################################################################################
# Compass
#################################################################################

class Compass(object):
    '''This class is responsible for handling i2c requests to a compass sensor'''

    def __init__(self,address):
        self.address = address

    # Aufgabe 2
    #
    # Diese Methode soll den Kompasswert auslesen und zurueckgeben. 
    def get_bearing(self):
        global bus
        """
        try:
            hi_b = bus.read_byte_data(self.address, 2)
        except Exception as e:
            print("Compass hi read exception", e)
            hi_b = 0
        try:
            lo_b = bus.read_byte_data(self.address, 3)
        except Exception as e:
            print("Compass lo read exception", e)
            lo_b = 0
        #return int.from_bytes(bytes([hi_b, lo_b]), byteorder="big") / 10
        return ((hi_b << 8) + lo_b)
        """
        try:
            comp_measure = bus.read_byte_data(self.address, 0x01)
            return comp_measure * 360/255
        except Exception as e:
            #print("Compass read exception", e)
            return -1

class CompassThread(threading.Thread):
    ''' Thread-class for holding compass data '''

    # Compass bearing value
    bearing = 0

    # Aufgabe 4
    #
    # Hier muss der Thread initialisiert werden.
    def __init__(self, address):
        threading.Thread.__init__(self)

        self.stopped = False

        self.compass = Compass(address)
        self.start()

    # Aufgabe 4
    #
    # Diese Methode soll den Kompasswert aktuell halten.
    def run(self):
        while not self.stopped:
            bear = self.compass.get_bearing()
            if (bear > 0):
                self.bearing = bear

    def stop(self):
        self.stopped = True

#################################################################################
# Infrared
#################################################################################

class Infrared(object):
    '''This class is responsible for handling i2c requests to an infrared sensor'''

    def __init__(self,address):
        global bus
        self.address = address
        try:
            #bus.write_byte_data(address, 0x00, 0x00)
            bus.write_byte(address, 0x00)
        except Exception as e:
            #print("Infrared write exception", e)
            pass
        
    # Aufgabe 2 
    #
    # In dieser Methode soll der gemessene Spannungswert des Infrarotsensors ausgelesen werden.
    def get_voltage(self):
        global bus
        # 0x00 to 0xFF
        readsucc = True
        try:
            readval = bus.read_byte_data(self.address, 0x00)
        except Exception as e:
            #print("Infrared read exception", e)
            readsucc = False
            #readval = 0
        # 0 to 5 (V)
        if readsucc:
            return readval * 5 / 255
        else:
            return -1

    # Aufgabe 3
    #
    # Der Spannungswert soll in einen Distanzwert umgerechnet werden.
    def get_distance(self):
        # L = 1 / (dist + 0.42)   -->   dist = (1/L - 0.42)
        # V = m * L + b   -->   L = (V - b)/m
        # linear approximation, okay for dist > 10
        # 0.02 -> 0.62
        x0 = 0.02
        y0 = 0.62
        # 0.08 -> 2.12
        x1 = 0.08
        y1 = 2.12
        m = (y1 - y0) / (x1 - x0)
        b = y0 - x0 * m
        V = self.get_voltage()
        L = (V - b) / m
        dist = 1/L - 0.42
        if (dist > 10 and dist < 80):
            return (1/L - 0.42)
        else:
            return -1


class InfraredThread(threading.Thread):
    ''' Thread-class for holding Infrared data '''

    # distance to an obstacle in cm
    distance = 0

    # length of parking space in cm
    parking_space_length = 0

    # Aufgabe 4
    #
    # Hier muss der Thread initialisiert werden.
    def __init__(self, address, encoder=None):
        threading.Thread.__init__(self)

        self.stopped = False

        self.encoder = encoder
        self.infrared = Infrared(address)
        self.setDaemon(True)
        self.start()

    def run(self):
        while not self.stopped:
            self.read_infrared_value()
            self.calculate_parking_space_length()

    # Aufgabe 4
    #
    # Diese Methode soll den Infrarotwert aktuell halten
    def read_infrared_value(self):  
        volt = self.infrared.get_voltage()
        if (volt >= 0 or True):
            distance = self.infrared.get_distance()
            if distance > 0:
                self.distance = distance

    # Aufgabe 5
    #
    # Hier soll die Berechnung der Laenge der Parkluecke definiert werden
    def calculate_parking_space_length(self):
        THR_DISTANCE = 20 #cm

        # obstacle on the right, IR distance < THR_DISTANCE
        # (drive forward) wait until IR distance >= THR_DISTANCE
        while (self.distance < THR_DISTANCE):
            self.read_infrared_value()
            #print("obstacle on the right")
            sleep(1 / POLLING_FREQ)

        # obstacle ended, save current position
        gap_start_absolute = self.encoder.get_travelled_dist()
        print("gap start", gap_start_absolute)

        # (drive forward) wait until IR distance < THR_DISTANCE
        while (self.distance > THR_DISTANCE):
            #print("no obstacle")
            self.read_infrared_value()
            sleep(1 / POLLING_FREQ)

        # end of gap reached
        gap_end_absolute = self.encoder.get_travelled_dist()
        print("gap end", gap_end_absolute)

        # subtract gap start position from end position
        p_s_l = gap_end_absolute - gap_start_absolute
        if (p_s_l > 0):
            self.parking_space_length = p_s_l
            print("Parking space found:", self.parking_space_length)

    def parked(self):
        self.parking_space_length = 0

    def stop(self):
        self.stopped = True

#################################################################################
# Encoder
#################################################################################
    
class Encoder(object):
    ''' This class is responsible for handling encoder data '''

    # Aufgabe 2
    #
    D = 7
    # Wieviel cm betraegt ein einzelner Encoder-Schritt?
    STEP_LENGTH = math.pi * D / 16 # in cm

    # number of encoder steps
    counter = 0

    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.IN)
        GPIO.add_event_detect(self.pin, GPIO.BOTH, callback=self.count, bouncetime=1)

    # Aufgabe 2
    #
    # Jeder Flankenwechsel muss zur Berechnung der Entfernung gezaehlt werden. 
    # Definieren Sie alle dazu noetigen Methoden.

    def count(self, channel):
        print("step counter", self.counter)
        self.counter += 1

    # Aufgabe 2
    # 
    # Diese Methode soll die gesamte zurueckgelegte Distanz zurueckgeben.
    def get_travelled_dist(self):
        return self.counter * self.STEP_LENGTH

class EncoderThread(threading.Thread):
    ''' Thread-class for holding speed and distance data of all encoders'''

    # current speed.
    speed = 0

    # currently traversed distance.
    distance = 0

    # Aufgabe 4
    #
    # Hier muss der Thread initialisiert werden.
    def __init__(self, encoder):
        threading.Thread.__init__(self)

        self.stopped = False

        self.encoder = encoder
        self.setDaemon(True)
        self.start()


    def run(self):
        while not self.stopped:
            self.get_values()

    # Aufgabe 4
    #
    # Diese Methode soll die aktuelle Geschwindigkeit sowie die zurueckgelegte Distanz aktuell halten.
    def get_values(self):
        global POLLING_FREQ
        sleep(1/POLLING_FREQ)
        distance_new = self.encoder.get_travelled_dist()
        self.speed = (distance_new - self.distance) * POLLING_FREQ
        self.distance = distance_new


    def stop(self):
        self.stopped = True

#################################################################################
# Main Thread
#################################################################################   

if __name__ == "__main__":

    # The GPIO pin to which the encoder is connected
    encoder_pin = 23

    # Aufgabe 1
    #
    # Tragen Sie die i2c Adressen der Sensoren hier ein

    # The i2c addresses of front and rear ultrasound sensors
    ultrasonic_front_i2c_address = 0x70;
    ultrasonic_rear_i2c_address = 0x71;

    # The i2c address of the compass sensor
    compass_i2c_address = 0x60

    # The i2c address of the infrared sensor
    infrared_i2c_address = 0x4f

    # Aufgabe 6
    # 
    # Hier sollen saemtlichen Messwerte periodisch auf der Konsole ausgegeben werden.

    enc = Encoder(encoder_pin)
    # threads start automatically in init
    u_t1 = UltrasonicThread(ultrasonic_front_i2c_address)
    u_t2 = UltrasonicThread(ultrasonic_rear_i2c_address)
    i_t = InfraredThread(infrared_i2c_address, enc)
    c_t = CompassThread(compass_i2c_address)

    e_t = EncoderThread(enc)

    while True:
        """
        print("encoder distance", e_t.distance, "\n",
              "encoder speed", e_t.speed, "\n",
              "compass bearing", c_t.bearing, "\n",
              "distance (front, back, side)", "(", u_t1.distance, u_t2.distance, i_t.distance, ")", "\n",
              "front brightness", u_t1.brightness, "\n",
              "parking space length", i_t.parking_space_length, "\n",
              )
        """
        sleep(0.1)
