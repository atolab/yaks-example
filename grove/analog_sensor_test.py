import time
import grovepi
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-p", "--pin", required=True,
                                help="GrovePi Pin")
args = vars(ap.parse_args())

pin = int(args['pin'])

while True:
    try:
        value = grovepi.analogRead(pin)
        print("value = {}".format(value))
        time.sleep(.5)

    except IOError:
        print ("Error")
