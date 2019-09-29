from yaks import Yaks, Encoding, Change, ChangeKind
import argparse
import cv2
import time
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("-z", "--zenoh", type=str, default="127.0.0.1",
                help="location of the ZENOH router")
ap.add_argument("-p", "--prefix", type=str, default="/demo/facerecog")
ap.add_argument("-d", "--delay", type=float, default=0.05,
                help="delay between each refresh")
args = vars(ap.parse_args())

cams = {}


def faces_listener(kvs):
    for k, v in kvs:
        chunks = k.split('/')
        cam = chunks[-2]
        face = int(chunks[-1])

        if cam not in cams:
            cams[cam] = {}
        if face not in cams[cam]:
            cams[cam][face] = {"img": b'', "name": "", "time": 0}

        cams[cam][face]["img"] = v.get_value().get_value()
        cams[cam][face]["time"] = time.time()


def names_listener(kvs):
    for k, v in kvs:
        chunks = k.split('/')
        cam = chunks[-3]
        face = int(chunks[-2])

        if cam not in cams:
            cams[cam] = {}
        if face not in cams[cam]:
            cams[cam][face] = {"img": b'', "name": "", "time": 0}

        cams[cam][face]["name"] = v.get_value().get_value()


print("[INFO] Connecting to yaks...")
y = Yaks.login(args['zenoh'])
ws = y.workspace('/')
ws.subscribe(args['prefix'] + "/faces/*/*", faces_listener)
ws.subscribe(args['prefix'] + "/faces/*/*/name", names_listener)

kvs = ws.get(args['prefix'] + "/faces/*/*/name", encoding=Encoding.STRING)
names_listener(map(lambda x: (x[0], Change(ChangeKind.PUT, 0, x[1])), kvs))

while True:
    now = time.time()

    for cam in list(cams):
        faces = cams[cam]
        vbuf = np.zeros((250, 1000, 3), np.uint8)
        for face in list(faces):
            if faces[face]["time"] > now - 0.2:
                npImage = np.array(faces[face]["img"])
                matImage = cv2.imdecode(npImage, 1)
                h, w, _ = matImage.shape
                vbuf[40:40+h, 200*face:200*face+w] = matImage

                name = faces[face]["name"]
                color = (0, 0, 255) if name == "Unknown" else (0, 255, 0)
                cv2.putText(vbuf,
                            name,
                            (200*face + 2, 18),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.75,
                            color,
                            2)

        cv2.imshow("Cam #" + cam, vbuf)

    time.sleep(args['delay'])

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

cv2.destroyAllWindows()
y.logout()
