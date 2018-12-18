from yaks import YAKS
import argparse
import json

ap = argparse.ArgumentParser()
ap.add_argument("-s", "--selector", required=True,
                help="the subscription selector")
ap.add_argument("-y", "--yaks", type=str, default="127.0.0.1",
                help="the YAKS instance")
args = vars(ap.parse_args())

def listener(kvs):    
    for kv in kvs:
        d = json.loads(kv['value'])
        print(d)

base_uri = '/'
ys = YAKS(args['yaks'])
acs = ys.create_access(base_uri)
acs.subscribe(args['selector'], listener)
input('Press a key to exit...')