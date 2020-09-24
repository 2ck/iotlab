from decimal import *

USE_IP_ID = True

BUFFER_SIZE = 1400

getcontext().prec = 10


def abschaetzung_owd(data1, data2):
    f1 = open(data1, "r")
    f2 = open(data2, "r")
    data_line1 = f1.readlines()
    data_line2 = f2.readlines()
    f1.close()
    f2.close()
    if len(data_line1) < len(data_line2):
        sume= Decimal(0)
        for i in range(len(data_line1)):
            time1, _ = data_line1[i].split(" ")
            time2, _ = data_line2[-i].split(" ")
            sume += abs(abs(Decimal(time1)) - abs(Decimal(time2)))
        return sume / Decimal(len(data_line1))
    else:
        sume = Decimal(0)
        for i in range(len(data_line2)):
            time1, _ = data_line2[i].split(" ")
            time2, _ = data_line1[-i].split(" ")
            abs(abs(Decimal(time1)) - abs(Decimal(time2)))
        return sume / Decimal(len(data_line2))

f1 = open("ipid_sequence_numbers_wlanudp.log", "r")
f2 = open("ipid_sequence_numbers_wlan_piudp.log", "r")

lines1 = f1.readlines()
f1.close()

lines2 = f2.readlines()
f2.close()

packet_dict = {}

# pi / sender
for line in lines2:
    split = line.split(" ")
    time = split[0]
    num = split[1]
    # todo only do if startswith 0x
    if USE_IP_ID:
        num = int(num[0:len(num)-1], 16)
    else:
        num = num[0:len(num)-1]
    packet_dict[num] = Decimal(time)
    #print(num, Decimal(time))


delay_dict = {}

# laptop / receiver
for line in lines1:
    split = line.split(" ")
    time = split[0]
    num = split[1]
    if USE_IP_ID:
        num = int(num[0:len(num)-1], 16)
    else:
        num = num[0:len(num)-1]
    if num in packet_dict.keys():
        delay_dict[num] = abs(packet_dict[num] - Decimal(time))
        #print(num, delay_dict[num])

    """
    delay_dict:
    20  159
    21  160
    22  161
    1   162
    2   163
    """


lasttime = sorted(packet_dict.values())[-1] 
firsttime = sorted(packet_dict.values())[0]
timediff = Decimal(lasttime) - Decimal(firsttime)

totalsize = 0
n = len(delay_dict)
if USE_IP_ID:
    totalsize = BUFFER_SIZE * n
else:
    totalsize = Decimal(sorted(packet_dict.keys())[-1])

print(totalsize, timediff)

print("Bitrate", totalsize/timediff)
avg = sum(delay_dict.values()) / n
var = sum([((abs(x) - avg) ** 2) for x in delay_dict.values()]) / n
print("Werte:", n)
print("Mittelwert (us):", avg * Decimal(1e6)) #1e6
print("Standardabweichung (us):", var ** Decimal(0.5) * Decimal(1e6))
