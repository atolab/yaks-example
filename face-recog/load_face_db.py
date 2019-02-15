# python3 load_face_db.py --path /demo/cv/face/signature -d face-sig-db/adlink.json 
from yaks import Yaks
from yaks import Encoding
from yaks import Value
import sys
import json
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dataset", required=True,
                help="path to input face database")
ap.add_argument("-p", "--path", required=True,
                help="path at which the faces have to be loaded")
ap.add_argument("-y", "--yaks", type=str, default="127.0.0.1",
                help="address of the yaks service to use")
args = vars(ap.parse_args())


def main(face_db):
    locator = args['yaks']
    ys = Yaks.login(locator)
    base_uri = args['path']
    # storage = ys.create_storage(base_uri)
    ws = ys.workspace(base_uri)
    for (k,vs) in face_db.items(): 
        for j,v in enumerate (vs):
            uri = '{}/{}/{}'.format(base_uri, k, j)
            print('> Inserting face {}'.format(uri)) 
            sv = json.dumps(v)
            ws.put(uri, Value(sv, encoding=Encoding.STRING))

    ys.logout()

if __name__ == '__main__':
    f = open(args['dataset'])
    faces = json.load(f)
    main(faces)
