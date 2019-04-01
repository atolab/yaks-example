# USAGE
# python3 recognize.py --cascade haarcascade_frontalface_default.xml --yaks 127.0.0.1 \
# --faces /demo/smart-home/<home>/vision/signature \
# --recog /demo/smart-home/<home>/vision/recognised

# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2
from yaks import Yaks
from yaks import Encoding
from yaks import Value, ChangeKind
import ast
import numpy as np
import json
import jsonpickle

data = {}
data['encodings'] = []
data['names'] = []


class TemporalSet(object):
    def __init__(self, interval):
        self.faces = {}
        self.interval = interval      

    def add_item(self, face):        
        self.faces[face] = time.time()
   
    def actualise(self):
        now = time.time()
        ofs = []
        for (f, t) in self.faces.items():
            if (t < now - self.interval):
                ofs.append(f)
        
        for f in ofs:
            del self.faces[f]
    
    def get_items(self):
        return [f for (f, _) in self.faces.items()]

def add_face_to_data(fdata, key, value):
    a, b, c = key.partition(uri_prefix)
    name, sep, num = c.partition('/')
    fdata['names'].append(name)
    a = ast.literal_eval(value)
    fdata['encodings'].append(a)


def update_face_data(kcs):
    print('Updating face data')
    for (k,c) in kcs:
        if c.kind == ChangeKind.PUT:
            key = k
            value = c.value.value
            add_face_to_data(data, key, value)
    
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--cascade", required=True,
                help="path to where the face cascade resides")
ap.add_argument("-y", "--yaks", type=str, default="127.0.0.1",
                help="the YAKS instance")                
ap.add_argument("-i", "--dinterval", type=float, default=2.1,
                help="detection interval")                                
ap.add_argument("-f", "--faces", required=True,
                help="The path indicating the faced that will have to be recognised")
ap.add_argument("-r", "--recog", required=True,
                help="The path indicating where recognised faces will be stored")                
args = vars(ap.parse_args())

print("[INFO] Connecting to YAKS ")


ys = Yaks.login(args['yaks'])
base_uri = args['faces']
recog_uri = args['recog']
detection_interval = args['dinterval']
uri_prefix = '{}/'.format(base_uri)
ws = ys.workspace('/')
uri = "{}/**".format(base_uri)
print("[INFO] Retrieving Faces Signatures")
fs = ws.get(uri, encoding=Encoding.STRING)

face_set = TemporalSet(detection_interval)

for (k,v) in fs:    
    add_face_to_data(data, k, v.value)
    print('Loaded data for face: {}'.format(k))

ws.subscribe(uri, update_face_data)

# load the known faces and embeddings along with OpenCV's Haar
# cascade for face detection
print("[INFO] loading encodings + face detector...")



detector = cv2.CascadeClassifier(args["cascade"])

# initialize the video stream and allow the camera sensor to warm up
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
# vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)

# start the FPS counter
fps = FPS().start()

# loop over frames from the video file stream
while True:
    # grab the frame from the threaded video stream and resize it
    # to 500px (to speedup processing)
    frame = vs.read()
    frame = imutils.resize(frame, width=500)

    # convert the input frame from (1) BGR to grayscale (for face
    # detection) and (2) from BGR to RGB (for face recognition)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # detect faces in the grayscale frame
    rects = detector.detectMultiScale(gray, scaleFactor=1.1,
                                      minNeighbors=5, minSize=(30, 30),
                                      flags=cv2.CASCADE_SCALE_IMAGE)

    # OpenCV returns bounding box coordinates in (x, y, w, h) order
    # but we need them in (top, right, bottom, left) order, so we
    # need to do a bit of reordering
    boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

    # compute the facial embeddings for each face bounding box
    encodings = face_recognition.face_encodings(rgb, boxes)

    names = []

    # loop over the facial embeddings
    for encoding in encodings:
        # attempt to match each face in the input image to our known
        # encodings

        matches = face_recognition.compare_faces(data["encodings"],
                                                 encoding)
        name = "Unknown"

        # check to see if we have found a match
        if True in matches:
            # find the indexes of all matched faces then initialize a
            # dictionary to count the total number of times each face
            # was matched
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}

            # loop over the matched indexes and maintain a count for
            # each recognized face face
            for i in matchedIdxs:
                name = data["names"][i]
                counts[name] = counts.get(name, 0) + 1

            # determine the recognized face with the largest number
            # of votes (note: in the event of an unlikely tie Python
            # will select first entry in the dictionary)
            name = max(counts, key=counts.get)

        # update the list of names        
        names.append(name)
        
    last_detection_set = str(face_set.get_items())
    for i in range(0 , len(names)):
        face_set.add_item(names[i])

    face_set.actualise()
    new_detection_set = str(face_set.get_items())
    if (new_detection_set != last_detection_set):
        print("New faces recognised {}".format(new_detection_set))  
        ws.put(recog_uri, Value(new_detection_set, encoding=Encoding.STRING))
        
    # loop over the recognized faces
    for ((top, right, bottom, left), name) in zip(boxes, names):
        # draw the predicted face name on the image
        cv2.rectangle(frame, (left, top), (right, bottom),
                      (0, 255, 0), 2)
        y = top - 15 if top - 15 > 15 else top + 15
        cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                    0.75, (0, 255, 0), 2)

    # display the image to our screen
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

    # update the FPS counter
    fps.update()

# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()