# python3 message_board.py --mboard /demo/smart-home/casa/message-boards 

from yaks import Yaks
from yaks import Value, Encoding
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-b", "--mboard", required=True,
                help="The message board URI")
ap.add_argument("-y", "--yaks", type=str, default="127.0.0.1",
                help="the YAKS instance")
args = vars(ap.parse_args())


board_uri = args['mboard']

if board_uri[len(board_uri) -1] != '/':
  board_uri = board_uri + '/'

print("URI : {}", board_uri)
y = Yaks.login(args['yaks'])
ws = y.workspace(board_uri)

def handle_post(c):
  name = input("> To: ")
  msg = input("> Message:\n")
  ws.put(board_uri + name, Value(msg, Encoding.STRING))

def print_board_msgs(kvs):
  l = len(board_uri)
  for (k,msg) in kvs: 
    name = k[l:len(k)]
    print("To: {}\n{}".format(name, msg))

def handle_list(c):
  kvs = ws.get(board_uri + "*")
  print_board_msgs(kvs)

def handle_query(c):
  q = input(">> Query: ")
  kvs = ws.get(q)
  print_board_msgs(kvs)

def handle_error(c):
  print("Invalid command: {}".format(c))

print("starting loop")
while True:
  print("[post, list, query, exit]")
  cmd = input('>')
  print(cmd)
  handler = {
    'post' : lambda c :  handle_post(c),
    'list' : lambda c : handle_list(c),
    'query' : lambda c : handle_query(c),
    'exit' : lambda c : exit(0),    
  }.get(cmd, handle_error)
  handler(cmd)
