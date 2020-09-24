#!/bin/bash

tcpdump -n -i wlp4s0 udp -w $1 &

python server.py -t UDP &

sleep 90

killall tcpdump
killall python
