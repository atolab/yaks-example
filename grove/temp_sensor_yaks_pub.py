from yaks import Yaks
from yaks import Value, ChangeKind, Encoding
import argparse
import time
import grovepi

period = 500000
ap = argparse.ArgumentParser()
ap.add_argument("-y", "--yaks", type=str, default="127.0.0.1",
                                help="the YAKS instance")
ap.add_argument("-u", "--uri", required=True,
                                        help="the publication path")
ap.add_argument("-p", "--pin", required=True,
                                help="GrovePi Pin")

args = vars(ap.parse_args())

pin = int(args['pin'])

y = Yaks.login(args['yaks'])
path = args['uri']
ws = y.workspace('/')

while True:
    try:
        value = grovepi.temp(pin, '1.2')
        print("value = {}".format(value))
        ws.put(path, Value(str(value), encoding=Encoding.STRING))
        time.sleep(.5)

    except IOError:
        print ("Error")
                                   
