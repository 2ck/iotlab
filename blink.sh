#!/bin/bash

while true
do
    # red LED / port 17
    echo "1" > /sys/class/gpio/gpio17/value
    sleep "1"
    echo "0" > /sys/class/gpio/gpio17/value
    # green LED / port 18
    echo "1" > /sys/class/gpio/gpio18/value
    sleep "1"
    echo "0" > /sys/class/gpio/gpio18/value
done
