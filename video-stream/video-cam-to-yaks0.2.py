import zenoh
from yaks import Yaks, Selector, Path, Workspace, Encoding, Value
import argparse
from imutils.video import VideoStream
import imutils
import time
import pickle
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("-y", "--yaks", type=str, default="127.0.0.1:7887", help="The Yaks server")
ap.add_argument("-p", "--path", type=str, default="/demo/video", help="The path to which frames are published")
args = vars(ap.parse_args())

print("[INFO] Connecting to yaks...")
y = Yaks.login(args['yaks'])
ws = y.workspace('/')

print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
time.sleep(2.0)

while True:
    frame = vs.read()
    frame = imutils.resize(frame, width=190)
    cv2.imshow("PUB", frame)
    buf = pickle.dumps(frame)
    ws.put(args['path'], Value(buf, Encoding.RAW))
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

cv2.destroyAllWindows()
vs.stop()
z.close()
