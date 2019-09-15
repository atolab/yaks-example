from yaks import Yaks
from yaks import Encoding
from yaks import Value
import sys
import json
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-z", "--zenoh", type=str, default="127.0.0.1",
                help="location of the ZENOH router")
ap.add_argument("-d", "--dataset", required=True,
                help="vectors dataset location")
ap.add_argument("-p", "--prefix", type=str, default="/demo/facerecog",
                help="resources prefix")
args = vars(ap.parse_args())


def main(face_db):
    locator = args['zenoh']
    ys = Yaks.login(locator)
    ws = ys.workspace(args['prefix'])
    for k, vs in face_db.items():
        for j, v in enumerate(vs):
            uri = '{}/vectors/{}/{}'.format(args['prefix'], k, j)
            print('> Inserting face {}'.format(uri))
            sv = json.dumps(v)
            ws.put(uri, Value(sv, encoding=Encoding.STRING))

    ys.logout()


if __name__ == '__main__':
    f = open(args['dataset'])
    faces = json.load(f)
    main(faces)
