#!/usr/bin/env python

#######################################################################
#                            Aufgabe 1                                #
#######################################################################

import pygame
import math
import enum

import servo_ctrl

import wiikt_main
import signal


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

speed_max = 11
angle_max = 45


# start main pygame event processing loop here
pygame.display.init()

# set up the pygame screen enviroment
screen = pygame.display.set_mode((width, height))

# get a clock to generate frequent behaviour
clock = pygame.time.Clock()


# initialize servo control
motor = servo_ctrl.Motor()
steering = servo_ctrl.Steering()

# start wiimote thread
wii_control = wiikt_main.Wii_Control(1/freq)
signal.signal(signal.SIGINT, wiikt_main.signal_handler)
wii_control.start()


# States of the keys
keystates = {'quit':False,
             'accelforw':False, 'accelback':False,
             'brake':False,
             'steerleft':False, 'steerright':False,
             'motoron':False
             }

# mouse or keyboard control
class CTRL_SCHEME(enum.Enum):
    KEYBD = 1
    MOUSE = 2
    WIIMT = 3
    WIIMT_ALT = 4
    def next(self):
        cls = self.__class__
        members = list(cls)
        index = (members.index(self) + 1) % len(members)
        return members[index]

control = CTRL_SCHEME.KEYBD

def calculate_acceleration(speed):
    mu = speed_max/2
    sig = 2.5
    a = 2.6
    acc = a * ( 1 - 1/2 * (1 + math.erf((abs(speed) - mu) / (math.sqrt(2 * sig * sig)))) )
    return acc

def calculate_friction(speed):
    mu = speed_max/2
    sig = 4
    f = -1
    fric = f / 2 * (1 + math.erf((abs(speed) - mu) / (math.sqrt(2 * sig * sig))))
    return fric


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

def brake():
    global speed_cur, speed_max, freq
    speed_new = 0
    if speed_cur > 0:
        speed_new = speed_cur - 4.5 / freq
        speed_new = max(speed_new, 0)
    if speed_cur < 0:
        speed_new = speed_cur + 4.5 / freq
        speed_new = min(speed_new, 0)
    speed_cur = speed_new

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

def friction():
    global speed_cur, speed_max, freq
    speed_new = 0
    fric = abs(calculate_friction(speed_cur))
    if speed_cur >= 0:
        speed_new = speed_cur - fric / freq
        speed_new = max(speed_new, 0)
    if speed_cur < 0:
        speed_new = speed_cur + fric / freq
        speed_new = min(speed_new, 0)
    speed_cur = speed_new

def steer_left():
    global angle_cur, angle_max, freq
    angle_new = 0
    angle_new = angle_cur + 300 / freq
    angle_cur = min(angle_new, angle_max)

def steer_right():
    global angle_cur, angle_max, freq
    angle_new = 0
    angle_new = angle_cur - 300 / freq
    angle_cur = max(angle_new, -angle_max)

def steer_normalize():
    global angle_cur, angle_max
    if angle_cur > 0:
        steer_right()
    if angle_cur < 0:
        steer_left()
    if abs(angle_cur) < 300 / freq:
        angle_cur = 0
        

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

def wiimote_leds(a,b,c,d):
    wii_control.wiimote.SetLEDs(a,b,c,d) 

def get_phi(x, y):
    phi = 0
    if x > 0:
        phi = math.atan(y / x)
    elif x < 0:
        if y >= 0:
            phi = math.atan(y / x) + math.pi
        else:
            phi = math.atan(y / x) - math.pi
    else:
        phi = math.copysign(math.pi / 2, y)
    return phi

def get_ang_wii():
    global angle_max
    global wii_control
    x,y,z = wii_control.wiimote.getAccelState()
    #r = math.sqrt(x ** 2 + y ** 2 + z ** 2)
    phi = 0
    thr_xy = 25
    if (abs(x) > thr_xy or abs(y) > thr_xy):
        #phi = get_phi(x, y)
        phi = math.atan2(y, x)
        print("atan result", phi)
        phi *= 180 / math.pi
        if (phi >= 0 and phi < 90):
            phi = 90 - phi
        if (phi < 0 and phi > -90):
            phi = -90 - phi
        print("correct phi", phi)
    ang = phi * 45 / 20 # the lower this factor the faster the turning
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

def low_pass(cur, last):
    w = 0.04 # 0 < w <= 1
    return (w * cur + (1 - w) * last)

def amplify(val):
    a = 0.5
    n = 1
    return (a * (val ** n) + (1 - a) * val)

running = True
pygame.mouse.set_pos(width/2, height/2)
try:
    while running:
        # set clock frequency
        clock.tick(freq);
        
        # save the last speed for analysis
        last = speed_cur

        # apply simulated friction
        if control == CTRL_SCHEME.KEYBD:
            friction()

        # get mouse position
        mx, my = get_pos()

        if control == CTRL_SCHEME.MOUSE:
            motor.set_speed(speed_cur)
            steering.set_angle(angle_cur)
     
        if control == CTRL_SCHEME.WIIMT:
            # set LEDs to reflect current speed
            wiimote_leds(int(speed_cur > 0),
                         int(speed_cur > speed_max/3),
                         int(speed_cur > 2 * speed_max/3),
                         int(speed_cur >= speed_max))

            wms = wii_control.wiimote.WiimoteState
            # controls are weird because the remote is held at a 90 degree angle
            # forward
            if wms.ButtonState.Right:
                speed_cur = min(speed_cur + 1, speed_max)
            if wms.ButtonState.Left:
                speed_cur = max(speed_cur - 1, 0)
            # left
            if wms.ButtonState.Up:
                angle_cur = min(angle_cur + 5, angle_max)
            if wms.ButtonState.Down:
                angle_cur = max(angle_cur - 5, -angle_max)

            steering.set_angle(angle_cur)

            # set speed with buttons 1 and 2
            if wms.ButtonState.One:
                motor.set_speed(speed_cur)
            if wms.ButtonState.Two:
                motor.set_speed(-speed_cur)

        if control == CTRL_SCHEME.WIIMT_ALT:
            # set LEDs to reflect current speed
            wiimote_leds(int(speed_cur > 0),
                         int(speed_cur > speed_max/3),
                         int(speed_cur > 2 * speed_max/3),
                         int(speed_cur >= speed_max))

            angle_cur = low_pass(get_ang_wii(), angle_cur)
            steering.set_angle(amplify(angle_cur))

            # set motor to active with button B
            if wms.ButtonState.B:
                speed_cur = get_speed_wii()
                motor.set_speed(speed_cur)


        # process input events
        for event in pygame.event.get():

            # exit on quit
            if event.type == pygame.QUIT:
                running = False

            # check for key down events (press)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    keystates['quit'] = True
                if event.key == pygame.K_m:
                    control = control.next()
                if event.key == pygame.K_BACKSPACE:
                    reset()
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

            # check for mouse down events
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    keystates['motoron'] = True

            # check for key up events (release)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_q:
                    keystates['quit'] = False
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

            # check for mouse up events
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    keystates['motoron'] = False

        # do something about the key states here, now that the event queue has been processed
        if keystates['quit']:
            running = False
            # doesn't work, why? TODO
            #wiikt_main.running = False
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
            angle_cur = get_ang_mouse(mx)
            if keystates['motoron']:
                speed_cur = get_speed_mouse(my)
        
        print("({0:.2f},{1:.2f} --> {2:.2f})".format(speed_cur, angle_cur, (speed_cur - last) / delta))
    
except KeyboardInterrupt:
    print("Exiting through keyboard event (CTRL + C)")
    
signal.pause()
wii_control.join()

# gracefully exit pygame here
pygame.quit()
