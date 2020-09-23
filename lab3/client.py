import socket

#IP un PORT des Server
IP = '192.168.0.10'
PORT = 1200

#unterschütze Addresstypen (IPv4, IPv6, lokalen Adressen)
address_familes = (socket.AF_INET, socket.AF_INET6, socket.AF_UNIX)

#Unterschütze Sockettypen (TCP, UDP, Raw( ohne Type))
socket_types = (socket.SOCK_STREAM, socket.SOCK_DGRAM, socket.SOCK_RAW)

#passende Address und socket wählen
address_family = address_familes[0]
socket_type = socket_types[0]

#Erstellen eines socket (TCP und UDP)
sock = socket.socket(address_family, socket_type)

#Verbinden zu einem Server-Socket (Nur TCP)

sock.connect((IP, PORT))

#Sende immer an durch Tastatur gegebene Nachricht an der Server
while True:
    #message = input("gebe ein Nachricht ein: ")
    message = b"Hello"
    #TCP
    sock.send(message)
    #UDP
    sock.sendto(message, (IP, PORT))
