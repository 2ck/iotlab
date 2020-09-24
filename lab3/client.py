import socket
import subprocess
import time

import argparse

parser = argparse.ArgumentParser(description="empty")
parser.add_argument("--type", "-t", type=str, help="TCP or UDP", default="TCP")

parser.add_argument("--rtimeout", "-rt", type=int, default=0)
parser.add_argument("--rfps", type=int, default=20)
parser.add_argument("--rwidth", "-rw", type=int, default=1280)
parser.add_argument("--rheight", "-rh", type=int, default=720)
parser.add_argument("--rbitrate", "-rb", type=int, default=2000000)


args = parser.parse_args()
tcp = True
if args.type == "UDP":
    tcp = False

#IP un PORT des Server
#IP = '172.23.90.118'
IP = '192.168.1.118'
PORT = 8080

BUFFER_SIZE = 4000

#unterstuetze Addresstypen (IPv4, IPv6, lokalen Adressen)
address_familes = (socket.AF_INET, socket.AF_INET6, socket.AF_UNIX)

#Unterstuetze Sockettypen (TCP, UDP, Raw( ohne Type))
socket_types = (socket.SOCK_STREAM, socket.SOCK_DGRAM, socket.SOCK_RAW)

#passende Address und socket waehlen
address_family = address_familes[0]
if tcp:
    socket_type = socket_types[0]
else:
    socket_type = socket_types[1]

#Erstellen eines socket (TCP und UDP)
sock = socket.socket(address_family, socket_type)

#Verbinden zu einem Server-Socket (Nur TCP)

if tcp:
    sock.connect((IP, PORT))


# raspivid
cmd_raspivid = "raspivid -t {} -fps {} -w {} -h {} -b {} -o - ".format(
        args.rtimeout, args.rfps, args.rwidth, args.rheight, args.rbitrate)
rasprocess = subprocess.Popen(cmd_raspivid, shell=True, stdout=subprocess.PIPE)

while True:
    data = rasprocess.stdout.read(BUFFER_SIZE)
    if tcp:
        sock.send(data)
    else:
        sock.sendto(data, (IP, PORT))
