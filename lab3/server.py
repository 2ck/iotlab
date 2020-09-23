import socket
import subprocess

import argparse

parser = argparse.ArgumentParser(description="empty")
parser.add_argument("--type", "-t", type=str, help="TCP or UDP", default="TCP")


args = parser.parse_args()
tcp = True
if args.type == "UDP":
    tcp = False

#Port des Servers
PORT = 8080

#Lesepuffergroesse
BUFFER_SIZE = 1400

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

#Maximal Anzahl der Verbindungen in Warteschlange
backlog = 1

#Erstellen eines socket (TCP und UDP)
sock = socket.socket(address_family, socket_type)
sock.bind(('', PORT))

#Lausche am Socket auf eingehende Verbindungen (Nur TCP)
if tcp:
    sock.listen(backlog)
    clientsocket, address = sock.accept()

# mplayer
cmd_mplayer = "mplayer -vo xv -fps 25 -cache 512 - "
mprocess = subprocess.Popen(cmd_mplayer, shell=True, stdin=subprocess.PIPE)

#Daten (der Groesse BUFFER_SIZE) aus dem Socket holen und ausgeben
while True:
    #TCP
    if tcp:
        data = clientsocket.recv(BUFFER_SIZE)
        #print(data)
        mprocess.stdin.write(data)
    else:
        #UDP
        data, address = sock.recvfrom(BUFFER_SIZE)
        mprocess.stdin.write(data)
