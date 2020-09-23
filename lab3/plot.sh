#!/bin/bash

gnuplot -p << EOF

#set terminal postscript eps color
set terminal png

set xlabel "time (unix)"
set ylabel "packets"

set output "plot.png"
set datafile separator ' '

plot "$1" using 1:2 with lines title "laptop", \
"$2" using 1:2 with lines title "pi"
EOF
