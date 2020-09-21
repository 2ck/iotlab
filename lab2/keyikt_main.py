#!/usr/bin/env python

#######################################################################
#                            Aufgabe 1                                #
#######################################################################

import pygame

width = 400
height = 200

freq = 50  # Sets the frequency of input procession
delta = 1.0 / freq # time per step
acc = 2.6  # Max acceleration of the car (per sec.)
dec = 4.5  # Max deceleration of the car (per sec.)
frict = -1  # max friction
angle_acc = 300  # max change of angle (per sec.)

speed_cur = 0
angle_cur = 0


# start main pygame event processing loop here
pygame.display.init()

# set up the pygame screen enviroment
screen = pygame.display.set_mode((width, height))

# get a clock to generate frequent behaviour
clock = pygame.time.Clock()


# States of the keys
keystates = {'quit':False, 'accelforw':False, 'accelback':False, 'brake':False}



def accelerate_forward():
    global speed_cur, freq
    speed = 0
    if speed_cur >= 0:
        speed = speed_cur + 2.6 / freq
        speed_cur = min(speed, 11)

def accelerate_backward():
    global speed_cur, freq
    speed = 0
    if speed_cur <= 0:
        speed = speed_cur - 2.6 / freq
        speed_cur = max(speed, -11)

def brake():
    global speed_cur, freq
    speed = 0
    if speed_cur >= 0:
        speed = speed_cur - 4.5 / freq
        speed = max(speed, 0)
    if speed_cur < 0:
        speed = speed_cur + 4.5 / freq
        speed = min(speed, 0)
    speed_cur = speed

def reset_speed():
    global speed_cur
    speed_cur = 0
    #print("Speed reset to 0")


running = True
try:
    while running:
        # set clock frequency
        clock.tick(freq);
        
        # save the last speed 4 analysis
        last = speed_cur
     
        # process input events
        for event in pygame.event.get():

            # exit on quit
            if event.type == pygame.QUIT:
                running = False

            # check for key down events (press)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    keystates['quit'] = True
                if event.key == pygame.K_BACKSPACE:
                    reset_speed()
                if event.key == pygame.K_w:
                    keystates['accelforw'] = True
                if event.key == pygame.K_s:
                    keystates['accelback'] = True
                if event.key == pygame.K_SPACE:
                    keystates['brake'] = True

            # check for key up events (release)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_q:
                    keystates['quit'] = False
                if event.key == pygame.K_w:
                    keystates['accelforw'] = False
                if event.key == pygame.K_s:
                    keystates['accelback'] = False
                if event.key == pygame.K_SPACE:
                    keystates['brake'] = False

        # do something about the key states here, now that the event queue has been processed
        if keystates['quit']:
            running = False
        if keystates['accelforw']:
            accelerate_forward()
        if keystates['accelback']:
            accelerate_backward()
        if keystates['brake']:
            brake()
        
        print("({},{} --> {})".format(speed_cur, angle_cur, (speed_cur - last) / delta))
    
except KeyboardInterrupt:
    print("Exiting through keyboard event (CTRL + C)")
    
# gracefully exit pygame here
pygame.quit()
