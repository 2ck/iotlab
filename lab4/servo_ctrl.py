#!/usr/bin/env python

#######################################################################
#                            Aufgabe 1.3                              #
#######################################################################

import gpio_class

def write(servo, pulse):
    gpio_class.write(servo, pulse)

class Motor(object):
    PWM_PIN = 1     # GPIO pin 11
    min_pulse = 100
    max_pulse = 200
    def __init__(self, servo=PWM_PIN):
        self.servo = servo
    def set_speed(self, speed):
        pulse = speed * 50 / 11 + 150
        pulse = min(max(pulse, self.min_pulse), self.max_pulse)
        #print("Motor:", pulse)
        write(self.servo, pulse)
    def stop(self):
        write(self.servo, 150)

class Steering(object):
    PWM_PIN = 2     # GPIO pin 12
    min_pulse = 100
    max_pulse = 200
    def __init__(self, servo=PWM_PIN):
        self.servo = servo
    def set_angle(self, angle):
        pulse = angle * 40 / 45 + 155
        pulse = min(max(pulse, self.min_pulse), self.max_pulse)
        #print("Servo:", pulse)
        write(self.servo, pulse)
    def stop(self):
        write(self.servo, 155)


if __name__ == "__main__":
    motor = Motor()
    steering = Steering()

    speed = float(input("Set speed: "))
    motor.set_speed(speed)
    angle = float(input("Set angle: "))
    steering.set_angle(angle)
