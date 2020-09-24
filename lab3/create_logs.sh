#!/bin/bash

tshark -r $1 -Y "tcp.port == 8080 && ip.src == $3 && udp.length > 50" -T fields -E separator=/s -e frame.time_epoch -e tcp.seq > sequence_numbers$4.log

tshark -r $2 -Y "tcp.port == 8080 && ip.src == $3 && udp.length > 50" -T fields -E separator=/s -e frame.time_epoch -e tcp.seq > sequence_numbers_pi$4.log
