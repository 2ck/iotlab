#!/bin/bash

sudo tcpdump -n -i wlp4s0 udp -w report_wlan.pcap &

python server.py -t UDP &

sleep 90

sudo killall tcpdump
killall python
