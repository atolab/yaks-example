from yaks import Yaks
from yaks import Value, ChangeKind
import argparse
import json

ap = argparse.ArgumentParser()
ap.add_argument("-s", "--selector", required=True,
                help="the subscription selector")
ap.add_argument("-y", "--yaks", type=str, default="127.0.0.1",
                help="the YAKS instance")
args = vars(ap.parse_args())

def listener(kcs):    
    for (k,c) in kcs:
        if c.kind == ChangeKind.PUT:
                # d = json.loads(c.value.value)
                print(c.value.value)

base_uri = '/'
y = Yaks.login(args['yaks'])
workspace = y.workspace('/')
workspace.subscribe(args['selector'], listener)
input('Press a key to exit...')