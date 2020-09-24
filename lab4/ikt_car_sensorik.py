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
        self.address = address
    
    # Aufgabe 2
    #
    # Diese Methode soll ein Datenbyte an den Ultraschallsensor senden um eine Messung zu starten
    def write(self,value):
        global bus
        bus.write_byte_data(self.address, 0x00, value)

    # Aufgabe 2
    #
    # Diese Methode soll den Lichtwert auslesen und zurueckgeben.
    def get_brightness(self):
        global bus
        return bus.read_byte_data(self.address, 0x01)

    # Aufgabe 2
    #
    # Diese Methode soll die Entfernung auslesen und zurueckgeben. 
    def get_distance(self):
        global bus
        hi_b = bus.read_byte_data(self.address, 0x02)
        lo_b = bus.read_byte_data(self.address, 0x03)
        print("ultrasonic", hi_b, lo_b)
        return int.from_bytes(bytes([hi_b, lo_b]), byteorder="big")

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

        self.ultrasonic = Ultrasonic(address)
        self.setDaemon(True)
        self.start()

    # Aufgabe 4
    #
    # Schreiben Sie die Messwerte in die lokalen Variablen
    def run(self):
        while not self.stopped:
            # measure in cm
            self.ultrasonic.write(0x51)
            # measurement takes 65ms max
            sleep(0.065)

            distance = self.ultrasonic.get_distance()
            brightness = self.ultrasonic.get_brightness()
            
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
        hi_b = bus.read_byte_data(self.address, 2)
        lo_b = bus.read_byte_data(self.address, 3)
        print("compass", hi_b, lo_b)
        return int.from_bytes(bytes([hi_b, lo_b]), byteorder="big") / 10

class CompassThread(threading.Thread):
    ''' Thread-class for holding compass data '''

    # Compass bearing value
    bearing = 0

    # Aufgabe 4
    #
    # Hier muss der Thread initialisiert werden.
    def __init__(self, address):
        threading.Thread.__init__(self)

        self.compass = Compass(address)
        self.start()

    # Aufgabe 4
    #
    # Diese Methode soll den Kompasswert aktuell halten.
    def run(self):
        while not self.stopped:
            bearing = self.compass.get_bearing()

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
        bus.write_byte(address, 0x00)
        
    # Aufgabe 2 
    #
    # In dieser Methode soll der gemessene Spannungswert des Infrarotsensors ausgelesen werden.
    def get_voltage(self):
        global bus
        return bus.read_byte_data(self.address, 0x00)

    # Aufgabe 3
    #
    # Der Spannungswert soll in einen Distanzwert umgerechnet werden.
    def get_distance(self):
        # V = 1 / ( 1/dist + 0.42)   -->   dist = 1/(1/V - 0.42)
        V = self.get_voltage()
        return (1 / (1/V - 0.42))


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
        self.encoder = encoder
        self.infrared = Infrared(address)
        self.setDaemon(True)
        self.start()

    def run(self):
        while not self.stopped:
            read_infrared_value()
            calculate_parking_space_length()

    # Aufgabe 4
    #
    # Diese Methode soll den Infrarotwert aktuell halten
    def read_infrared_value(self):  
        distance = self.infrared.get_distance()

    # Aufgabe 5
    #
    # Hier soll die Berechnung der Laenge der Parkluecke definiert werden
    def calculate_parking_space_length(self):
        THR_DISTANCE = 20 #cm
        # obstacle on the right, IR distance < THR_DISTANCE
        # (drive forward) wait until IR distance >= THR_DISTANCE
        while (distance < THR_DISTANCE):
            sleep(1 / POLLING_FREQ)
        # obstacle ended, save current position
        gap_start_absolute = self.encoder.get_travelled_dist()
        # (drive forward) wait until IR distance < THR_DISTANCE
        while (distance > THR_DISTANCE):
            sleep(1 / POLLING_FREQ)
        # end of gap reached
        gap_end_absolute = self.encoder.get_travelled_dist()
        # subtract gap start position from end position
        parking_space_length = gap_end_absolute - gap_start_absolute

    def stop(self):
        self.stopped = True

#################################################################################
# Encoder
#################################################################################
    
class Encoder(object):
    ''' This class is responsible for handling encoder data '''

    # Aufgabe 2
    #
    # TODO
    D = 7
    # Wieviel cm betraegt ein einzelner Encoder-Schritt?
    STEP_LENGTH = math.pi * D / 16 # in cm

    # number of encoder steps
    count = 0

    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.IN)
        GPIO.add_event_detect(self.pin, GPIO.BOTH, callback=self.count, bouncetime=1)

    # Aufgabe 2
    #
    # Jeder Flankenwechsel muss zur Berechnung der Entfernung gezaehlt werden. 
    # Definieren Sie alle dazu noetigen Methoden.

    def count(channel):
        count += 1

    # Aufgabe 2
    # 
    # Diese Methode soll die gesamte zurueckgelegte Distanz zurueckgeben.
    def get_travelled_dist(self):
        return count * STEP_LENGTH

class EncoderThread(threading.Thread):
    ''' Thread-class for holding speed and distance data of all encoders'''

    # current speed.
    speed = 0

    # currently traversed distance.
    distance = 0

    # Aufgabe 4
    #
    # Hier muss der Thread initialisiert werden.
    # TODO do we really want to call init with the encoder class already created?
    def __init__(self, encoder):
        threading.Thread.__init__(self)
        self.encoder = encoder
        self.setDaemon(True)
        self.start()


    def run(self):
        while not self.stopped:
            get_values()

    # Aufgabe 4
    #
    # Diese Methode soll die aktuelle Geschwindigkeit sowie die zurueckgelegte Distanz aktuell halten.
    def get_values(self):
        global POLLING_FREQ
        distance_new = self.encoder.get_travelled_dist()
        speed = (distance_new - distance) * POLLING_FREQ
        distance = distance_new


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
        print("encoder distance" e_t.distance,
              "encoder speed", e_t.speed,
              "compass bearing", c_t.bearing,
              "distance (front, back, side)", "(", u_t1.distance, u_t2.distance, i_t.distance, ")",
              "front brightness", u_t1.brightness,
              "parking space length", i_t.parking_space_length,
              sep = " | ")
        sleep(1 / POLLING_FREQ)
