#!/usr/bin/python
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import io
import json

import threading
from ikt_car_sensorik import *
import servo_ctrl
from math import acos, sqrt, degrees


PARKING_SPEED = 5
currently_parking = False
do_parking = False
stop_parking = False

# Aufgabe 4
#
# Der Tornado Webserver soll die Datei index.html am Port 8081 zur Verfügung stellen
from tornado.options import define, options
define("port", default=8081, help="run on the given port", type=int)

class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("index.html")

# Aufgabe 3
#
# Der Tornado Webserver muss eine Liste der clients verwalten.  
class WebSocketHandler(tornado.websocket.WebSocketHandler):
    '''Definition der Operationen des WebSocket Servers'''

    print("hello WebSocketHandler")

    def open(self):
        print("new connection:", self.request.remote_ip)
        clients.append(self)

    def on_message(self, message):
        global do_parking, stop_parking
        print("message received:", message)
        if (message == "park"):
            print("Start parking process")
            do_parking = True
        elif (message == "stoppark"):
            print("Stop parking process")
            stop_parking = True
        else:
            json_message = {}
            json_message["response"] = message
            json_message = json.dumps(json_message)
            self.write_message(json_message)

    def on_close(self):
        print("connection closed")
        clients.remove(self)


class DataThread(threading.Thread):
    '''Thread zum Senden der Zustandsdaten an alle Clients aus der Client-Liste'''

    # Aufgabe 3
    #
    # Hier muss der Thread initialisiert werden.
    def __init__(self):
        threading.Thread.__init__(self)

        self.stopped = False

        address_ultrasonic_front = 0x70
        address_ultrasonic_back = 0x71 
        address_compass = 0x60
        address_infrared = 0x4F
        encoder_pin = 23
        self.set_sensorik(address_ultrasonic_front, address_ultrasonic_back, address_compass, address_infrared, encoder_pin)
    
    # Aufgabe 3
    #
    # Erstellen Sie hier Instanzen von Klassen aus dem ersten Teilversuch       
    def set_sensorik(self, address_ultrasonic_front, address_ultrasonic_back, address_compass, address_infrared, encoder_pin):
        enc = Encoder(encoder_pin)

        self.u_t1 = UltrasonicThread(address_ultrasonic_front)
        self.u_t2 = UltrasonicThread(address_ultrasonic_back)
        self.c_t = CompassThread(address_compass)
        self.i_t = InfraredThread(address_infrared, enc)
        self.e_t = EncoderThread(enc)

    # Aufgabe 3
    #
    # Hier muessen die Sensorwerte ausgelesen und an alle Clients des Webservers verschickt werden.
    def run(self):
        global currently_parking
        disthelper = 0
        while not self.stopped:
            parkdist = -1
            if currently_parking:
                parkdist = self.e_t.distance - disthelper
            else:
                disthelper = self.e_t.distance
            json_message = {
                "brightness":self.u_t1.brightness,
                "front_distance":self.u_t1.distance,
                "rear_distance":self.u_t2.distance,
                "bearing":self.c_t.bearing,
                "side_distance":self.i_t.distance,
                "parking_space_length":self.i_t.parking_space_length,
                "driven_distance":self.e_t.distance,
                "speed":self.e_t.speed,
                "parkdist":parkdist
                }
            for c in clients:
                try:
                    c.write_message(json_message)
                except:
                    print("write exception")


    def stop(self):
        self.stopped = True

class DrivingThread(threading.Thread):
    '''Thread zum Fahren des Autos'''

    # Einparken
    #
    # Hier muss der Thread initialisiert werden.
    def __init__(self, datathread):
        threading.Thread.__init__(self)

        self.stopped = False

        self.datathread = datathread

        self.motor = servo_ctrl.Motor()
        self.steering = servo_ctrl.Steering()

        # Breite des Autos
        self.w = 15
        # Abstand zum Nachbarauto
        self.p = 10
        # Abstand der Achsen
        f = 30
        # Abstand von Hinterachse zu Heck
        b = 5
        # Wendekreis
        self.r = self.p + 3 * self.w / 2
        self.l = sqrt(2 * self.r * self.w + f ** 2) + b
        print("min length", self.l)

    def check_stop(self):
        global stop_parking
        THR_FRONTBACK = 20
        # check for obstacle
        if self.datathread.u_t1.distance < THR_FRONTBACK or self.datathread.u_t2.distance < THR_FRONTBACK:
            stop_parking = True
        if stop_parking:
            self.motor.stop()
            self.steering.stop()
            stop_parking = False

            return True
        return False

    def parking_process(self):
        global PARKING_SPEED, do_parking, currently_parking

        currently_parking = True

        # radencoder broken, zeit statt distanz benutzen
        DO_USE_TIME = True
        PARKING_SLEEP_TIME = 5

        starttime = int(time())
        start_angle = self.datathread.c_t.bearing
        start_pos = self.datathread.e_t.distance

        do_parking = False
        if self.check_stop():
            return
        alpha = acos(1 - (self.p + self.w) / (2 * self.r))
        alpha = degrees(alpha)
        circlepath = 2 * math.pi * self.r * alpha/360
        # rueckwaerts fahren bis ende der luecke
        # 
        self.motor.stop()

        # ----- parken startet -----
        # steering alpha, weiter rueckwaerts fahren
        self.steering.set_angle(alpha)
        self.motor.set_speed(-PARKING_SPEED)
        # bis wir 2 pi r * alpha/360 gefahren sind
        circlepath = 0.5 # just for testing
        if DO_USE_TIME:
            for i in range(1, 101):
                sleep(PARKING_SLEEP_TIME / 100)
                if self.check_stop():
                    return
        else:
            while (self.datathread.e_t.distance - start_pos < circlepath):
                if self.check_stop():
                    return
                #print(self.datathread.e_t.distance, circlepath)
        mid_pos = self.datathread.e_t.distance
        # steering -alpha, weiter rueckwaerts fahren
        self.steering.set_angle(-alpha)
        # bis wir noch mal 2 pi r * alpha/360 gefahren sind
        if DO_USE_TIME:
            for i in range(1, 101):
                sleep(PARKING_SLEEP_TIME / 100)
                if self.check_stop():
                    return
        else:
            while (self.datathread.e_t.distance - mid_pos < circlepath):
                if self.check_stop():
                    return
        # ----- parken fertig -----

        self.motor.stop()
        self.steering.stop()
        self.datathread.i_t.parked()

        # how long did parking take
        endtime = int(time())
        json_message = {"time":(endtime - starttime)}
        for c in clients:
            try:
                c.write_message(json_message)
                print("wrote park time message")
            except:
                print("write exception")
        print("Parking took", endtime - starttime, "seconds")

        # check if parallel
        end_angle = self.datathread.c_t.bearing
        ANGLE_DIFF_THR = 10
        if ((abs(end_angle - start_angle) < ANGLE_DIFF_THR) or (abs(abs(end_angle - start_angle) - 360) < ANGLE_DIFF_THR)):
            print("(Nearly) parallel:", start_angle, end_angle)
        else:
            print("Not parallel", start_angle, end_angle)

    # Einparken
    #
    # Definieren Sie einen Thread, der auf die ueber den Webserver erhaltenen Befehle reagiert und den Einparkprozess durchfuehrt
    def run(self):
        global do_parking, currently_parking
        while not self.stopped:
            #if (self.datathread.i_t.parking_space_length >= self.l and do_parking):
            if (do_parking):
                self.parking_process()
                currently_parking = False

    def stop(self):
        self.stopped = True
        for i in range(6, -1, -1):
            self.motor.set_speed(i)
            sleep(0.5)
        

if __name__ == "__main__":
    print("Main Thread started")
    clients = []
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[
            (r"/ws", WebSocketHandler),
            (r"/", IndexHandler),
            (r"/(.*)", tornado.web.StaticFileHandler, {"path": os.path.dirname(__file__)}),
            ])
    httpServer = tornado.httpserver.HTTPServer(app)
    httpServer.listen(options.port)
    print("Listening on port:", options.port)

    # Aufgabe 3
    #
    # Erstellen und starten Sie hier eine Instanz des DataThread und starten Sie den Webserver .
    datathread = DataThread()
    datathread.start()


    # Einparken
    #
    # Erstellen und starten Sie hier eine Instanz des DrivingThread, um das Einparken zu ermoeglichen.

    drivingthread = DrivingThread(datathread)
    drivingthread.start()
    # start io loop and join threads
    tornado.ioloop.IOLoop.instance().start()
    datathread.join()
    drivingthread.join()
