# 1.e)
Erstellen Sie ein Bashskript welches die beiden LEDs abwechselnd für eine Sekunde aufleuchten lässt.
```
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
```

# 1.f)
Erstellen Sie ein weiteres Bashskript, welches periodisch den Zustand des angeschlossenen Tasters ausgibt.
```
#!/bin/bash

while true
do
    # button / port 2
    cat /sys/class/gpio/gpio2/value
    sleep "1"
done
```


# 2.a)
```TODO```
