#!/usr/bin/env python

#######################################################################
#                            Aufgabe 1                                #
#######################################################################

import pygame
import math
import enum

import numpy as np

import servo_ctrl

import wiikt_main
import signal


# pygame window dimensions
width = 400
height = 200

# update rate for pygame and wiimote control thread
freq = 50           # Sets the frequency of input procession
delta = 1.0 / freq  # time per step

speed_cur = 0
angle_cur = 0

speed_max = 11
angle_max = 45

# filter and amplifier properties
w = 0.3            # 0 < w <= 1
alpha = 0.5
n = 1


# start main pygame event processing loop here
pygame.display.init()

# set up the pygame screen environment
screen = pygame.display.set_mode((width, height))

# get a clock to generate frequent behaviour
clock = pygame.time.Clock()

# states of the keys
keystates = {'quit':False,
             'accelforw':False, 'accelback':False,
             'brake':False,
             'steerleft':False, 'steerright':False,
             'motoron':False
             }

# mouse or keyboard control
class CTRL_SCHEME(enum.Enum):
    # keyboard control of simulation, no servo values written
    KEYBD = 1
    # mouse control of servos, click for speed
    MOUSE = 2
    # DPAD (sideways), set speed with <1> for forward and <2> for backward
    WIIMT = 3
    # tilt controls, press B to toggle motor activation TODO
    WIIMT_ALT = 4

    # iterator helper function
    def next(self):
        cls = self.__class__
        members = list(cls)
        index = (members.index(self) + 1) % len(members)
        return members[index]

# set default control scheme, TODO change to WIIMT_ALT when calibrate on load works
control = CTRL_SCHEME.KEYBD





##########################################
######## KEYBOARD SIMULATION MODE ########
#========================================#
#
# values for simulation

a = 2.6             # Max acceleration of the car (m/s^2)
d = 4.5             # Max deceleration of the car (m/s^2)
f = -1              # max friction
angle_acc = 300     # max change of angle (deg/s)

# functions for simulation

def calculate_acceleration(speed):
    global a
    mu = speed_max/2
    sig = 2.5
    acc = a * ( 1 - 1/2 * (1 + math.erf((abs(speed) - mu) / (math.sqrt(2 * sig * sig)))) )
    return acc

def accelerate_forward():
    global speed_cur, speed_max, freq
    speed_new = 0
    acc = calculate_acceleration(speed_cur)
    if speed_cur >= 0:
        speed_new = speed_cur + acc / freq
        speed_cur = min(speed_new, speed_max)

def accelerate_backward():
    global speed_cur, speed_max, freq
    speed_new = 0
    acc = calculate_acceleration(speed_cur)
    if speed_cur <= 0:
        speed_new = speed_cur - acc / freq
        speed_cur = max(speed_new, -speed_max)


def calculate_friction(speed):
    global f
    mu = speed_max/2
    sig = 4
    fric = f / 2 * (1 + math.erf((abs(speed) - mu) / (math.sqrt(2 * sig * sig))))
    return fric

def reduce_speed(decel):
    global speed_cur, freq
    speed_new = 0
    if speed_cur > 0:
        speed_new = speed_cur - decel / freq
        speed_new = max(speed_new, 0)
    if speed_cur < 0:
        speed_new = speed_cur + decel / freq
        speed_new = min(speed_new, 0)
    speed_cur = speed_new

def brake():
    global d
    reduce_speed(d)

def apply_friction():
    global speed_cur, speed_max, freq
    speed_new = 0
    fric = abs(calculate_friction(speed_cur))
    reduce_speed(fric)

def steer_left():
    global angle_cur, angle_max, angle_acc, freq
    angle_new = 0
    angle_new = angle_cur + angle_acc / freq
    angle_cur = min(angle_new, angle_max)

def steer_right():
    global angle_cur, angle_max, angle_acc, freq
    angle_new = 0
    angle_new = angle_cur - angle_acc / freq
    angle_cur = max(angle_new, -angle_max)

def steer_normalize():
    global angle_cur, angle_max, angle_acc
    if angle_cur > 0:
        steer_right()
    if angle_cur < 0:
        steer_left()
    # prevents alternation between +a and -a where abs(a) < the angle change per tick
    if abs(angle_cur) < angle_acc / freq:
        angle_cur = 0
#
#========================================#
######## KEYBOARD SIMULATION MODE ########
##########################################





##########################################
########    MOUSE CONTROL MODE    ########
#========================================#
#
# get mouse position in window and translate it so the (0, 0) is in the center
def get_pos():
    global width, height
    x, y = pygame.mouse.get_pos()
    newx = - (x - width / 2)
    newy = - (y - height / 2)
    return newx, newy

def get_ang_mouse(x):
    global angle_max, width
    ang = angle_max * x / (width / 2)
    return ang

def get_speed_mouse(y):
    global speed_max, height
    speed = speed_max * y / (height / 2)
    return speed
#
#========================================#
########    MOUSE CONTROL MODE    ########
##########################################





##########################################
########   WIIMOTE CONTROL MODE   ########
#========================================#
#
# functions for smoothing and amplifying the wiimote signal

def low_pass(cur, last):
    global w
    return (w * cur + (1 - w) * last)

def amplify(val):
    global alpha, n
    return (alpha * (val ** n) + (1 - alpha) * val)


# start wiimote thread, which updates at the same rate as the main thread
wii_control = wiikt_main.Wii_Control(freq)
# to kill thread on CTRL+C
signal.signal(signal.SIGINT, wiikt_main.signal_handler)
wii_control.start()

def wiimote_leds(speed):
    global speed_max, wii_control
    speed = abs(speed)
    wii_control.wiimote.SetLEDs(
            int(speed > 0),
            int(speed > speed_max/3),
            int(speed > 2 * speed_max/3),
            int(speed >= speed_max))


def sgn_helper(x):
    return 1 * (x > 0)

def get_ang_wii():
    global angle_max
    global wii_control
    global pygame
    x,y,z = wii_control.wiimote.getAccelState()

    vector1 = [1,0,0]
    vector2 = [x,y,z]
    unit_vector1 = vector1 / np.linalg.norm(vector1)
    unit_vector2 = vector2 / np.linalg.norm(vector2)

    dot_product = np.dot(unit_vector1, unit_vector2)

    angle = np.arccos(dot_product) #angle in radian
    if (y > 0):
        angle = angle - math.pi/2
        angle = -angle
    elif (y < 0):
        angle = angle - math.pi/2

    #r = math.sqrt(x ** 2 + y ** 2)
    phi = 0
    thr_xy = 20
    """
    # check if we're outside of the control deadzone
    if (abs(x) > thr_xy or abs(y) > thr_xy):
        if (x != 0):
            # atan(y/x) + pi * heaviside(-x) * sign(y)
            phi = math.atan(y / x) + math.pi * sgn_helper(-x) * math.copysign(1, y)
        else:
            phi = math.copysign(math.pi / 2, y) + math.pi * sgn_helper(-x) * math.copysign(1, y)
    """
    if (abs(x) > thr_xy or abs(y) > thr_xy):
        phi = angle
    # convert from rad to deg
    phi *= 180 / math.pi
    # convert from (what should be) [-90, 90] to [-45, 45]
    ang = phi * 45 / 40
    if ang >= 0:
        return min(ang, angle_max)
    else:
        return max(ang, -angle_max)

def get_speed_wii():
    global speed_max
    global wii_control
    x,y,z = wii_control.wiimote.getAccelState()
    thr_z = 10
    if (abs(z) < thr_z):
        z = 0
    speed = z * 11 / 50
    if speed >= 0:
        return min(speed, speed_max)
    else:
        return max(speed, -speed_max)
#
#========================================#
########   WIIMOTE CONTROL MODE   ########
##########################################





# initialize servo control
motor = servo_ctrl.Motor()
steering = servo_ctrl.Steering()


# reset speed, angle, and optionally the control scheme
def reset():
    global speed_cur, angle_cur
    global control
    global motor, steering
    speed_cur = 0
    angle_cur = 0
    # for safety, shouldn't be needed
    motor.set_speed(0)
    steering.set_angle(0)
    # reset mouse to the center of the window (0, 0)
    pygame.mouse.set_pos(width/2, height/2)
    #control = CTRL_SCHEME.KEYBD





running = True
# initialize the mouse position to the center / our (0, 0)
pygame.mouse.set_pos(width/2, height/2)

try:
    while running:
        # set clock frequency
        clock.tick(freq);
        
        # save the last speed for analysis
        last = speed_cur

        # get mouse position
        mx, my = get_pos()


        # apply simulated friction
        if control == CTRL_SCHEME.KEYBD:
            apply_friction()


        elif control == CTRL_SCHEME.MOUSE:
            angle_cur = get_ang_mouse(mx)
            steering.set_angle(angle_cur)
            # set the speed below, only if 'motoron' is True
            speed_cur = get_speed_mouse(my)
     

        elif control == CTRL_SCHEME.WIIMT:
            # set LEDs to reflect current speed
            wiimote_leds(speed_cur)

            wms = wii_control.wiimote.WiimoteState
            # angle and speed steps
            angs = 5
            spds = 0.5
            # controls are weird because the remote is held at a 90 degree angle
            # forward, backward    0 <= speed <= speed_max
            if wms.ButtonState.Right:
                speed_cur = min(speed_cur + spds, speed_max)
            if wms.ButtonState.Left:
                speed_cur = max(speed_cur - spds, 0)
            # left, right    -angle_max <= angle <= angle_max
            if wms.ButtonState.Up:
                angle_cur = min(angle_cur + angs, angle_max)
            if wms.ButtonState.Down:
                angle_cur = max(angle_cur - angs, -angle_max)

            # always set the angle
            steering.set_angle(angle_cur)

            # set speed with buttons 1 and 2
            if wms.ButtonState.One:
                motor.set_speed(speed_cur)
            if wms.ButtonState.Two:
                motor.set_speed(-speed_cur)


        elif control == CTRL_SCHEME.WIIMT_ALT:
            # set LEDs to reflect current speed
            wiimote_leds(speed_cur)

            # low_pass(current, last)
            angle_new = low_pass(get_ang_wii(), angle_cur)
            # lower thr to prevent going from -45 -> 45
            thr = 70
            if (abs(angle_new) - abs(angle_cur) < thr):
                angle_cur = angle_new
            # overwriting angle_cur with the amplified value would lead to overflows
            steering.set_angle(amplify(angle_cur))

            speed_cur = get_speed_wii()

            # set motor state to active with button B
            if wms.ButtonState.B:
                # TODO will this get rapidly toggled if the B button is held?
                # if so, use the version below
                #keystates['motoron'] = not keystates['motoron']
                keystates['motoron'] = True
            else:
                keystates['motoron'] = False



        # process input events
        for event in pygame.event.get():

            # exit on quit
            if event.type == pygame.QUIT:
                running = False

            ######## general key down and up events ########
            #
            if event.type == pygame.KEYDOWN:
                # quit
                if event.key == pygame.K_q:
                    keystates['quit'] = True
                # toggle control scheme
                if event.key == pygame.K_m:
                    control = control.next()
                # reset everything
                if event.key == pygame.K_BACKSPACE:
                    reset()

            # check for key up events (release)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_q:
                    keystates['quit'] = False
            #
            ################################################


            ######## FOR SIMULATION ########
            #
            if event.type == pygame.KEYDOWN:
                # acceleration and braking
                if event.key == pygame.K_w:
                    keystates['accelforw'] = True
                if event.key == pygame.K_s:
                    keystates['accelback'] = True
                if event.key == pygame.K_SPACE:
                    keystates['brake'] = True
                # steering
                if event.key == pygame.K_a:
                    keystates['steerleft'] = True
                if event.key == pygame.K_d:
                    keystates['steerright'] = True

            if event.type == pygame.KEYUP:
                # acceleration and braking
                if event.key == pygame.K_w:
                    keystates['accelforw'] = False
                if event.key == pygame.K_s:
                    keystates['accelback'] = False
                if event.key == pygame.K_SPACE:
                    keystates['brake'] = False
                # steering
                if event.key == pygame.K_a:
                    keystates['steerleft'] = False
                if event.key == pygame.K_d:
                    keystates['steerright'] = False
            #
            ################################


            ######## FOR MOUSE CONTROL ########
            #
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    keystates['motoron'] = True

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    keystates['motoron'] = False
            #
            ###################################


        # do something about the key states here, now that the event queue has been processed
        if keystates['quit']:
            # TODO does this work?
            wiikt_main.stop()
            running = False

        if control == CTRL_SCHEME.KEYBD:
            if keystates['accelforw']:
                accelerate_forward()
            if keystates['accelback']:
                accelerate_backward()
            if keystates['brake']:
                brake()

            if keystates['steerleft']:
                steer_left()
            elif keystates['steerright']:
                steer_right()
            else:
                steer_normalize()


        elif control == CTRL_SCHEME.MOUSE:
            if keystates['motoron']:
                motor.set_speed(speed_cur)

        elif control == CTRL_SCHEME.WIIMT_ALT:
            if keystates['motoron']:
                motor.set_speed(speed_cur)

        
        print("({0:.2f},{1:.2f} --> {2:.2f})".format(speed_cur, angle_cur, (speed_cur - last) / delta))
    
except KeyboardInterrupt:
    print("Exiting through keyboard event (CTRL + C)")
    
signal.pause()
wii_control.join()

# gracefully exit pygame here
pygame.quit()
