import imutils
from imutils import paths
from imutils.video import VideoStream
import numpy as np
import face_recognition
import argparse
import pickle
import cv2
import os
import json
from yaks import Yaks
from yaks import Encoding
from yaks import Value, ChangeKind

ap = argparse.ArgumentParser()
ap.add_argument("-n", "--name", required=True,
                help="The name of the person")
ap.add_argument("-y", "--yaks", type=str, default="127.0.0.1",
                help="the YAKS instance")  
ap.add_argument("-f", "--faces", required=True,
                help="The path indicating the faces that will have to be recognised")
ap.add_argument("-c", "--cascade", required=True,
                help="path to where the face cascade resides")
ap.add_argument("-d", "--detection-method", type=str, default="cnn",
                help="face detection model to use: either `hog` or `cnn`")
args = vars(ap.parse_args())

detector = cv2.CascadeClassifier(args['cascade'])

print("[INFO] Connecting to YAKS ")
ys = Yaks.login(args['yaks'])
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
        cv2.rectangle(frame, (rects[0][0], rects[0][1]), (rects[0][0]+rects[0][2], rects[0][1]+rects[0][3]),
                      (0, 255, 0), 2)
    
    cv2.putText(frame, "Press <space> to take picture <q> to quit.", (10, 250), 
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65, (0, 255, 0), 2)
    cv2.imshow("Register new face", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord(" "): 
        if len(rects) > 0:
            face = frame[rects[0][1]:rects[0][1]+rects[0][3], rects[0][0]:rects[0][0]+rects[0][2]]
            encoding = face_recognition.face_encodings(rgb, 
                [(rects[0][1], rects[0][0]+rects[0][2], rects[0][1]+rects[0][3], rects[0][0])])[0]
            elist = encoding.tolist()

            uri = "{}/**".format(args["faces"])
            fs = ws.get(uri, encoding=Encoding.STRING)
            counter = "0"
            for (k,_) in fs: 
                chunks=k.split('/')
                name=chunks[len(chunks) - 2]
                if name == args["name"]:
                    if int(counter) <= int(chunks[len(chunks) - 1]):
                        counter = str(int(chunks[len(chunks) - 1]) + 1)

            uri = '{}/{}/{}'.format(args["faces"], args["name"], counter)
            print('> Inserting face {}'.format(uri)) 
            ws.put(uri, Value(json.dumps(elist), encoding=Encoding.STRING))
            exit(0)
    if key == ord("q"):
        exit(0)
