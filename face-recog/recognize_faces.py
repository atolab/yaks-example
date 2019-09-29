import argparse
import time
import ast
import cv2
import numpy as np
import face_recognition
from yaks import Yaks, Encoding, Value, ChangeKind

ap = argparse.ArgumentParser()
ap.add_argument("-z", "--zenoh", type=str, default="127.0.0.1",
                help="location of the ZENOH router")
ap.add_argument("-q", "--quality", type=int, default=95,
                help="The quality of the published faces (0 - 100)")
ap.add_argument("-p", "--prefix", type=str, default="/demo/facerecog",
                help="The resources prefix")
ap.add_argument("-d", "--delay", type=float, default=0.2,
                help="delay between each recognition")
args = vars(ap.parse_args())

data = {}
data['encodings'] = []
data['names'] = []
cams = {}


def add_face_to_data(fdata, key, value):
    chunks = key.split('/')
    name = chunks[-2]
    num = chunks[-1]
    fdata['names'].append(name)
    a = ast.literal_eval(value)
    fdata['encodings'].append(a)


def update_face_data(kcs):
    for k, c in kcs:
        if c.kind == ChangeKind.PUT:
            print('Received face vector {}'.format(k))
            value = c.value.value
            add_face_to_data(data, k, value)


def faces_listener(kvs):
    for k, v in kvs:
        chunks = k.split('/')
        cam = chunks[-2]
        face = int(chunks[-1])

        if cam not in cams:
            cams[cam] = {}

        cams[cam][face] = v.get_value().get_value()


print("[INFO] Connecting to YAKS ")
ys = Yaks.login(args['zenoh'])
ws = ys.workspace('/')

print("[INFO] Retrieving faces vectors")
for k, v in ws.get(args['prefix'] + "/vectors/**", encoding=Encoding.STRING):
    add_face_to_data(data, k, v.value)

print("[INFO] Starting recognition...")
ws.subscribe(args['prefix'] + "/vectors/**", update_face_data)
ws.subscribe(args['prefix'] + "/faces/*/*", faces_listener)

while True:
    for cam in list(cams):
        faces = cams[cam]
        for face in list(faces):
            npImage = np.array(faces[face])
            matImage = cv2.imdecode(npImage, 1)
            rgb = cv2.cvtColor(matImage, cv2.COLOR_BGR2RGB)

            encodings = face_recognition.face_encodings(rgb)

            name = "Unknown"
            if len(encodings) > 0:
                matches = face_recognition.compare_faces(data["encodings"],
                                                         encodings[0])
                if True in matches:
                    matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                    counts = {}
                    for i in matchedIdxs:
                        name = data["names"][i]
                        counts[name] = counts.get(name, 0) + 1
                    name = max(counts, key=counts.get)

            path = args['prefix'] + "/faces/" + cam + "/" + str(face) + "/name"
            ws.put(path, Value(name, Encoding.STRING))

    time.sleep(args['delay'])
