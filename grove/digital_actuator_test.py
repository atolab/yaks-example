import time
import grovepi
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-p", "--pin", required=True,
                                help="GrovePi Pin")
args = vars(ap.parse_args())

pin = int(args['pin'])

grovepi.pinMode(pin,"OUTPUT")

while True:
    try:
        print ("write 1")
        grovepi.digitalWrite(pin,1)
        time.sleep(1)

        print ("write 0")
        grovepi.digitalWrite(pin,0)
        time.sleep(1)

    except KeyboardInterrupt:
        grovepi.digitalWrite(pin,0)
        break
    except IOError:
        print ("Error")
