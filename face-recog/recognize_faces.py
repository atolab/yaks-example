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
args = vars(ap.parse_args())

data = {}
data['encodings'] = []
data['names'] = []


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


state = {}

print("[INFO] Connecting to YAKS ")
ys = Yaks.login(args['zenoh'])
ws = ys.workspace('/')

print("[INFO] Retrieving Faces Vectors")
for k, v in ws.get(args['prefix'] + "/vectors/**", encoding=Encoding.STRING):
    add_face_to_data(data, k, v.value)

ws.subscribe(args['prefix'] + "/vectors/**", update_face_data)


def framelistener(kcs):
    for k, v in kcs:
        if v.kind == ChangeKind.PUT:
            frame = v.get_value().get_value()
            npImage = np.array(frame)
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

            if k in state:
                last_name, last_time = state[k]
                if name != "Unknown":
                    if last_name != name:
                        ws.put(k + "/name", Value(name, Encoding.STRING))
                    state[k] = (name, time.time())
                else:
                    if last_name != "Unknown"and last_time < time.time() - 0.1:
                        ws.put(k + "/name", Value(name, Encoding.STRING))
                        state[k] = (name, time.time())
            else:
                ws.put(k + "/name", Value(name, Encoding.STRING))
                state[k] = (name, time.time())


ws.subscribe(args['prefix'] + "/faces/*/*", framelistener)

while True:
    time.sleep(10)
