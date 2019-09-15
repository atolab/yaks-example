from yaks import *
import argparse
from imutils.video import VideoStream
import imutils
import time
import pickle
import cv2
import queue
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("-z", "--zenoh", type=str, default="127.0.0.1",
                help="location of the ZENOH router")
ap.add_argument("-p", "--path", type=str, default="/demo/video",
                help="The path to which frames are subscribed")
args = vars(ap.parse_args())

queue = queue.Queue()

def listener(kvs):
    for kv in kvs:
        queue.put(kv)

print("[INFO] Connecting to yaks...")
y = Yaks.login(args['yaks'])
ws = y.workspace('/')
ws.subscribe(args['path'], listener)

while True:
    k, v = queue.get()
    frame = v.get_value().get_value()
    npImage = np.array(frame)
    matImage = cv2.imdecode(npImage, 1)
    cv2.imshow("SUB " + k, matImage)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
        
cv2.destroyAllWindows()
z.close()
