import os

def change_pulse_width(servo, pw):
   os.system("echo {}={} > /dev/servoblaster".format(servo, pw))
