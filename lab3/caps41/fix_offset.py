from decimal import *


fn1 = "sequence_numbers_outside.log"
# smaller (-40min or something)
fn2 = "sequence_numbers_outside_pi.log"

f1 = open(fn1, "r")
f2 = open(fn2, "r")
out = open(fn2 + "modified", "w")

goodline = f1.readline()
goodtime = Decimal(goodline.split(" ")[0])

badline = f2.readline()
badtime = Decimal(badline.split(" ")[0])

timediff = goodtime - badtime


lines = f2.readlines()
f2.close()

for i in range(0, len(lines)):
    split = lines[i].split(" ")
    line = "{} {}".format(Decimal(split[0]) + timediff, split[1])
    out.write(line)

out.close()
