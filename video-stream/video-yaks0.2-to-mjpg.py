from yaks import *
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from imutils.video import VideoStream
import cv2
import imutils
import time
import argparse
import pickle
import queue

ap = argparse.ArgumentParser()
ap.add_argument("-y", "--yaks", type=str, default="127.0.0.1:7887", help="The Yaks server")
ap.add_argument("-p", "--path", type=str, default="/demo/video", help="The path to which frames are subscribed")
ap.add_argument("-t", "--httpport", type=int, default=8080, help="The http port")
args = vars(ap.parse_args())

mjpg_streams = []

def listener(kvs):
  for (_, v) in kvs: 
      frame = pickle.loads(v.get_value().get_value())
      ret, jpeg = cv2.imencode('.jpg', frame)
      buf=jpeg.tobytes()
      for stream in mjpg_streams:
        stream.wfile.write(b'--frame')
        stream.send_header('Content-type','image/jpeg')
        stream.send_header('Content-length',len(buf))
        stream.end_headers()
        stream.wfile.write(buf)
        stream.wfile.flush()

print("[INFO] Connecting to yaks...")
y = Yaks.login(args['yaks'])
ws = y.workspace('/')
ws.subscribe(args['path'], listener)

class CamHandler(BaseHTTPRequestHandler):
  def do_GET(self):
    print("Accept new mjpg stream consumer.")
    self.send_response(200)
    self.send_header('Content-type','multipart/x-mixed-replace; boundary=--frame')
    self.end_headers()
    mjpg_streams.append(self)
    while True:
      time.sleep(1000)

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""
    
if __name__ == '__main__':
  try:
    server = ThreadedHTTPServer(('', args["httpport"]), CamHandler)
    server.serve_forever()

  except KeyboardInterrupt:
    server.socket.close()