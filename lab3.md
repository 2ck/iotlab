# General
- "problems": latency and packet loss
    - multimedia: latency important, packet loss unimportant
    - email/web/ftp: latency unimportant, packet loss important

- streaming:
    - packet latency (!= latency)
    - jitter (standard deviation of packet latency)
    - playout delay (if not live streaming): compensate jitter and thus loss, but increase overall latency (buffering at the start for example)

# TCP and UDP
- TCP (transmission control protocol):
    - header 20B
        - sender + receiver port, sequence number, ack sn, window size, checksum
    - connection-oriented
        - client -> server: SYN, ISN
        - server -> client: SYN + ACK, ISN+1
        - client -> server: SYN, ISN+2
    - all packets arrive, order known
    - packets need to be ack-ed, resent if not
    - sliding window
        - receiver: advertised window
        - sender: congestion window
        - take minimum
    - slow start
        - start with 1 packet, increase cwnd exponentially
        - until missing (timeout) or double (wrong order) ack
    - congestion avoidance
        - additive increase, multiplicative decrease (of cwnd)
- UDP (user datagram protocol):
    - header 8B
    - no connection needed
    - packets may be lost, will not be resent
    - constant bit rate may be too high, but no rate control to mitigate that

# DCF (Distributed Coordination Function)
- DIFS: sender listens for availability
- backoff time: wait for random * slot time `[0, w-1]`, if still available then:
- preamble: send with low rate
- data: send with high rate
- SIFS: receiver waits
- ack: receiver sends ack

- multiple senders: random backoff time decides who goes first
- same backoff time: resend packets after timeout
- double contention window w, reset to minimum after successful transmission

# TCPdump, tshark, wireshark
- tcpdump: tcp, udp on interface into file, log or pcap
- tshark: command line version of wireshark
    - Y for filters (ip.{src,dst}, tcp.seq, ...)
    - ack flag = 0x010

# NTP
- analyze network performance: one way delay
- needs time synchronization of sender and receiver
- ntp service, /etc/ntp.conf
- test with ntpq -pn

# Gnuplot
- plot log/csv(?)
- output to eps or pdf


# Implementation
- python socket, subprocess, argparse for command line arguments
- raspivid on client, h264 stream, set fps, dimensions, bitrate, etc.
- mplayer on server, fps, cache size


- disable segmentation offloading with ethtool (split packets larger than maximum segment size)

- change to other WIFI with ifconfig/iwconfig
- check with ip r
