fn = raw_input("file to modify: ")
f = open(fn, "r")
out = open(fn + "modified", "w")

lines = f.readlines()
f.close()

for i in range(0, len(lines)):
    split = lines[i].split(" ")
    line = "{} {}".format(split[0], i)
    out.write(line + '\n')

out.close()
