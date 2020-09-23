f = open("sequence_numbers_piwlanudp.log", "r")
out = open("sequence_numbers_piwlanudp_modified.log", "w")

lines = f.readlines()
f.close()

for i in range(0, len(lines)):
    split = lines[i].split(" ")
    line = "{} {}".format(split[0], i)
    out.write(line + '\n')

out.close()
