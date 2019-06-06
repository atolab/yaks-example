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
import time
import cv2
from yaks import Yaks
from yaks import Encoding
from yaks import Value, ChangeKind
import ast
import numpy as np
import json
import os

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
                help="The path indicating the faces that will have to be recognised")
ap.add_argument("-s", "--source", required=True,
                help="The path indicating where frames should be subscribed")   
ap.add_argument("-r", "--recog", required=True,
                help="The path indicating where recognised faces will be stored")                
ap.add_argument("-w", "--width", type=int, default=450, 
                help="The width of the published faces")
ap.add_argument("-q", "--quality", type=int, default=95, 
                help="The quality of the published faces (0 - 100)")           
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
detector = cv2.CascadeClassifier(args['cascade'])

def framelistener(kcs):
    # print("frame")
    for (k,c) in kcs:
        if c.kind == ChangeKind.PUT:
            key = k
            value = c.value.value

            npImage = np.array(value)
            frame = cv2.imdecode(npImage, 1)

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            rects = detector.detectMultiScale(gray, scaleFactor=1.1,
                                            minNeighbors=5, minSize=(30, 30),
                                            flags=cv2.CASCADE_SCALE_IMAGE)

            boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

            encodings = face_recognition.face_encodings(rgb, boxes)

            names = []

            for encoding in encodings:
                matches = face_recognition.compare_faces(data["encodings"],
                                                        encoding)
                name = "Unknown"
                if True in matches:
                    matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                    counts = {}
                    
                    for i in matchedIdxs:
                        name = data["names"][i]
                        counts[name] = counts.get(name, 0) + 1
                    
                    name = max(counts, key=counts.get)
                
                names.append(name)
                
            last_detection_set = str(face_set.get_items())
            for i in range(0 , len(names)):
                face_set.add_item(names[i])

            face_set.actualise()
            new_detection_set = str(face_set.get_items())
            if (new_detection_set != last_detection_set):
                print("New faces recognised {}".format(new_detection_set))  
                ws.put(recog_uri, Value(new_detection_set, encoding=Encoding.STRING))
            
            faces=np.zeros((args["width"] * 2 // 3, args["width"],3), np.uint8)
            for ((name, (top, right, bottom, left)), i) in zip(sorted(zip(names, boxes)), range(len(names))):
                if i < 6:
                    face = frame[top:bottom, left:right]
                    face = imutils.resize(face, height=args["width"]//3, width=args["width"]//3)
                    cv2.putText(face, name, (2, 18) , cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 3)
                    cv2.putText(face, name, (2, 18) , cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 1)
                    faceheight, facewidth, _ = face.shape
                    if i < 3:
                        faces[0:faceheight, i*args["width"]//3:i*args["width"]//3+facewidth] = face
                    else:
                        faces[args["width"]//3:args["width"]//3+faceheight, (i-3)*args["width"]//3:(i-3)*args["width"]//3+facewidth] = face

            ret, jpeg = cv2.imencode('.jpg', faces, [int(cv2.IMWRITE_JPEG_QUALITY), args["quality"]])
            buf=jpeg.tobytes()
            ws.put(recog_uri+"/image", Value(buf, Encoding.RAW))
                
            # loop over the recognized faces
            for ((top, right, bottom, left), name) in zip(boxes, names):
                # draw the predicted face name on the image
                cv2.rectangle(frame, (left, top), (right, bottom),
                            (0, 255, 0), 2)
                y = top - 15 if top - 15 > 15 else top + 15
                cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                            0.75, (0, 255, 0), 2)

            # if the `q` key was pressed, break from the loop
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                exit(0)

ws.subscribe(args['source'], framelistener)

while True:
    time.sleep(10)

# # stop the timer and display FPS information
# print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
# print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# # do a bit of cleanup
# cv2.destroyAllWindows()
# vs.stop()