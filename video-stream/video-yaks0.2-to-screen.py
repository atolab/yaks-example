from yaks import *
import argparse
from imutils.video import VideoStream
import imutils
import time
import pickle
import cv2
import queue

ap = argparse.ArgumentParser()
ap.add_argument("-y", "--yaks", type=str, default="127.0.0.1:7887", help="The Yaks server")
ap.add_argument("-p", "--path", type=str, default="/demo/video", help="The path to which frames are subscribed")
args = vars(ap.parse_args())

queue = queue.Queue()

def listener(kvs):
    for (_, v) in kvs:
        frame = pickle.loads(v.get_value().get_value())
        queue.put(frame)

print("[INFO] Connecting to yaks...")
y = Yaks.login(args['yaks'])
ws = y.workspace('/')
ws.subscribe(args['path'], listener)

while True:
    frame = queue.get()
    cv2.imshow("SUB", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
        
cv2.destroyAllWindows()
z.close()
