import socket

#Port des Servers
PORT = 1200

#Lesepuffergröße
BUFFER_SIZE = 1400

#unterschütze Addresstypen (IPv4, IPv6, lokalen Adressen)
address_familes = (socket.AF_INET, socket.AF_INET6, socket.AF_UNIX)

#Unterschütze Sockettypen (TCP, UDP, Raw( ohne Type))
socket_types = (socket.SOCK_STREAM, socket.SOCK_DGRAM, socket.SOCK_RAW)

#passende Address und socket wählen
address_family = address_familes[0]
socket_type = socket_types[0]

#Maximal Anzahl der Verbindungen in Warteschlange
backlog = 1

#Erstellen eines socket (TCP und UDP)
sock = socket.socket(address_family, socket_type)
sock.bind(('', PORT))

#Lausche am Socket auf eingehende Verbindungen (Nur TCP)
sock.listen(backlog)
clientsocket, address = sock.accept()

#Daten (der Größe BUFFER_SIZE) aus dem Socket holen und ausgeben
while True:
    #TCP
    data = clientsocket.recv(BUFFER_SIZE)
    print(data)

    #UDP
    data, address = clientsocket.recvfrom(BUFFER_SIZE)
    print(data)