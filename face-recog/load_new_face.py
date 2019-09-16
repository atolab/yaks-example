import argparse
import time
import json
import cv2
import imutils
from imutils.video import VideoStream
import face_recognition
from yaks import Yaks, Encoding, Value

ap = argparse.ArgumentParser()
ap.add_argument("-n", "--name", required=True,
                help="The name of the person")
ap.add_argument("-z", "--zenoh", type=str, default="127.0.0.1",
                help="location of the ZENOH router")
ap.add_argument("-p", "--prefix", type=str, default="/demo/facerecog",
                help="The resources prefix")
ap.add_argument("-c", "--cascade", type=str,
                default="haarcascade_frontalface_default.xml",
                help="path to the face cascade file")
ap.add_argument("-d", "--detection-method", type=str, default="cnn",
                help="face detection model to use: either `hog` or `cnn`")
args = vars(ap.parse_args())

detector = cv2.CascadeClassifier(args['cascade'])

print("[INFO] Connecting to YAKS ")
ys = Yaks.login(args['zenoh'])
ws = ys.workspace('/')

vs = VideoStream(src=0).start()

while True:
    frame = vs.read()
    frame = imutils.resize(frame, width=500)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    rects = detector.detectMultiScale(gray, scaleFactor=1.1,
                                      minNeighbors=5, minSize=(30, 30),
                                      flags=cv2.CASCADE_SCALE_IMAGE)

    if len(rects) > 0:
        cv2.rectangle(frame,
                      (rects[0][0], rects[0][1]),
                      (rects[0][0]+rects[0][2], rects[0][1]+rects[0][3]),
                      (0, 255, 0), 2)

    cv2.putText(frame, "Press <space> to take picture <q> to quit.", (10, 250),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65, (0, 255, 0), 2)
    cv2.imshow("Register new face vector", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord(" "):
        if len(rects) > 0:
            face = frame[rects[0][1]:rects[0][1]+rects[0][3],
                         rects[0][0]:rects[0][0]+rects[0][2]]
            box = [(rects[0][1], rects[0][0]+rects[0][2],
                    rects[0][1]+rects[0][3], rects[0][0])]
            encoding = face_recognition.face_encodings(rgb, box)[0]
            elist = encoding.tolist()

            fs = ws.get(args["prefix"] + "/vectors/**",
                        encoding=Encoding.STRING)
            counter = 0
            for k, _ in fs:
                chunks = k.split('/')
                name = chunks[-2]
                if name == args["name"]:
                    if counter <= int(chunks[-1]):
                        counter = int(chunks[-1]) + 1

            uri = '{}/vectors/{}/{}'.format(
                args["prefix"], args["name"], str(counter))
            print('> Inserting face vector {}'.format(uri))
            ws.put(uri, Value(json.dumps(elist), encoding=Encoding.STRING))

    time.sleep(0.05)

    if key == ord("q"):
        exit(0)

vs.stop()
y.logout()
