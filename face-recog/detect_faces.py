import argparse
from imutils.video import VideoStream
import imutils
import time
import cv2
from yaks import Yaks, Encoding, Value
import zenoh
import binascii

ap = argparse.ArgumentParser()
ap.add_argument("-z", "--zenoh", type=str, default="127.0.0.1",
                help="location of the ZENOH router")
ap.add_argument("-w", "--width", type=int, default=200,
                help="width of the published faces")
ap.add_argument("-q", "--quality", type=int, default=95,
                help="quality of the published faces (0 - 100)")
ap.add_argument("-c", "--cascade", type=str,
                default="haarcascade_frontalface_default.xml",
                help="path to the face cascade file")
ap.add_argument("-d", "--delay", type=float, default=0.05,
                help="delay between each frame in seconds")
ap.add_argument("-p", "--prefix", type=str, default="/demo/facerecog",
                help="resources prefix")
args = vars(ap.parse_args())

jpeg_opts = [int(cv2.IMWRITE_JPEG_QUALITY), args["quality"]]

print("[INFO] Connecting to YAKS ")
ys = Yaks.login(args['zenoh'])
pid = binascii.hexlify(ys.rt.info()[zenoh.Z_INFO_PID_KEY]).decode('ascii')
ws = ys.workspace('/')

detector = cv2.CascadeClassifier(args['cascade'])

print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
time.sleep(1.0)

while True:
    raw = vs.read()
    frame = imutils.resize(raw, width=500)
    ratio = raw.shape[1]/500

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    rects = detector.detectMultiScale(gray, scaleFactor=1.1,
                                      minNeighbors=5, minSize=(30, 30),
                                      flags=cv2.CASCADE_SCALE_IMAGE)
    boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

    faces = zip(range(len(boxes)), sorted(boxes))

    for (i, (top, right, bottom, left)) in faces:
        face = raw[int(top*ratio):int(bottom*ratio),
                   int(left*ratio):int(right*ratio)]
        face = imutils.resize(face, height=args["width"], width=args["width"])
        _, jpeg = cv2.imencode('.jpg', face, jpeg_opts)
        buf = jpeg.tobytes()

        ws.put("{}/faces/{}/{}".format(args['prefix'], pid, i),
               Value(buf, Encoding.RAW))

    time.sleep(args["delay"])

vs.stop()
y.logout()
