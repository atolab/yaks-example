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
ap.add_argument("-o", "--out", type=str, default="frame.jpg", help="The file to which frames are saved")
args = vars(ap.parse_args())

def listener(kvs):
    for (_, v) in kvs:
        filehandle = open(args['out'], 'wb')  
        filehandle.write(v.get_value().get_value())  
        filehandle.close()  

print("[INFO] Connecting to yaks...")
y = Yaks.login(args['yaks'])
ws = y.workspace('/')
ws.subscribe(args['path'], listener)

while True:
    time.sleep(10)
        
cv2.destroyAllWindows()
z.close()
