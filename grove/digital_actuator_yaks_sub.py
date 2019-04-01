from yaks import Yaks
from yaks import Value, ChangeKind
import argparse
import time
import grovepi

period = 500000
ap = argparse.ArgumentParser()
ap.add_argument("-y", "--yaks", type=str, default="127.0.0.1",
                                help="the YAKS instance")
ap.add_argument("-s", "--selector", required=True,
                                        help="the subscription selector")
ap.add_argument("-f", "--filter", required=True, help="Content filter")
ap.add_argument("-p", "--pin", required=True,
                                help="GrovePi Pin")

args = vars(ap.parse_args())

pin = int(args['pin'])
grovepi.pinMode(pin, "OUTPUT")

def listener(kcs):
    for (k,c) in kcs:
        if c.kind == ChangeKind.PUT:
            print ("recv "  + c.value.value)
            if args['filter'] in c.value.value :
                print ("  write 1")
                grovepi.digitalWrite(pin,1)
            else: 
                print ("  write 0")
                grovepi.digitalWrite(pin,0)
        else:
            print ("  write 0")
            grovepi.digitalWrite(pin,0)

y = Yaks.login(args['yaks'])
selector = args['selector']
ws = y.workspace('/')

ws.subscribe(selector, listener)

while True:
    time.sleep(5)

                                   
