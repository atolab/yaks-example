from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from imutils.video import VideoStream
import cv2
import imutils
import time
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-t", "--httpport", type=int, default=8080, help="The http port")
ap.add_argument("-w", "--width", type=int, default=500, help="The width of the published frames")
ap.add_argument("-q", "--quality", type=int, default=95, help="The quality of the published frames (0 - 100)")
args = vars(ap.parse_args())

print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()

class CamHandler(BaseHTTPRequestHandler):
  def do_GET(self):
    self.send_response(200)
    self.send_header('Content-type','multipart/x-mixed-replace; boundary=--frame')
    self.end_headers()
    while True:
      try:
        frame = vs.read()
        frame = imutils.resize(frame, width=args["width"])
        ret, jpeg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), args["quality"]])
        buf=jpeg.tobytes()
        self.wfile.write(b'--frame')
        self.send_header('Content-type','image/jpeg')
        self.send_header('Content-length',len(buf))
        self.end_headers()
        self.wfile.write(buf)
      except KeyboardInterrupt:
        break

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""
    
if __name__ == '__main__':
	try:
		server = ThreadedHTTPServer(('localhost', args["httpport"]), CamHandler)
		server.serve_forever()
	except KeyboardInterrupt:
		server.socket.close()