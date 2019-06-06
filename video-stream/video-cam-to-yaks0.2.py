from yaks import Yaks, Selector, Path, Workspace, Encoding, Value
import argparse
from imutils.video import VideoStream
import imutils
import time
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("-y", "--yaks", type=str, default="127.0.0.1:7887", help="The Yaks server")
ap.add_argument("-p", "--path", type=str, default="/demo/video", help="The path to which frames are published")
ap.add_argument("-d", "--delay", type=float, default=0.01, help="The delay between each frame in seconds")
ap.add_argument("-w", "--width", type=int, default=500, help="The width of the published frames")
ap.add_argument("-q", "--quality", type=int, default=95, help="The quality of the published frames (0 - 100)")
ap.add_argument("-n", "--nodisplay", action='store_true', help="Disable the video display")  
args = vars(ap.parse_args())

print("[INFO] Connecting to yaks...")
y = Yaks.login(args['yaks'])
ws = y.workspace('/')

print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
time.sleep(2.0)

while True:
    frame = vs.read()
    frame = imutils.resize(frame, width=args["width"]) 
    if not args['nodisplay']:
        cv2.imshow("PUB", frame)
    ret, jpeg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), args["quality"]])
    buf=jpeg.tobytes()
    ws.put(args['path'], Value(buf, Encoding.RAW))
    
    time.sleep(args["delay"])
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

cv2.destroyAllWindows()
vs.stop()
z.close()
