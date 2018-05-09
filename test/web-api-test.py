#!/usr/bin/env python3

import json, code, sys, readline, os.path, atexit, time
sys.path.insert(0, '.')
from sakura.common.io import AttrCallAggregator, RemoteAPIForwarder
from websocket import create_connection

if len(sys.argv) < 2:
    print('Usage: %s <hub_web_port> [<session_secret>]' % sys.argv[0])
    sys.exit()

web_port = int(sys.argv[1])
if len(sys.argv) > 2:
    session_secret = sys.argv[2]
    ws_path = "ws://localhost:%d/websockets/sessions/connect/%s" % \
                    (web_port, session_secret)
else:
    ws_path = "ws://localhost:%d/websockets/sessions/new" % web_port

# Persistent command history.
histfile = os.path.join(os.environ["HOME"], ".web-api-history")
try:
    readline.read_history_file(histfile)
except IOError:
    # Existing history file can't be read.
    pass
atexit.register(readline.write_history_file, histfile)

class FileWSock(object):
    def __init__(self, url):
        self.url = url
        self.connected = False
        self.ever_connected = False
        self.msg = ''
        self.wsock = None
    def connect(self):
        self.wsock = create_connection(self.url)
        self.connected = True
    def write(self, s):
        self.msg += s
    def read(self):
        if not self.ever_connected:
            print('Connecting...', end='', flush=True)
        while True:
            try:
                if self.connected:
                    # we send the message only now
                    # in order to ease exception catching
                    self.wsock.send(self.msg)
                    # ... and read the answer
                    msg = self.wsock.recv()
                    if msg == None:
                        msg = ''
                    self.msg = ''   # ok, done
                    return msg
                else:
                    self.connect()
                    if self.ever_connected:
                        print(' ok, repaired.')
                    else:
                        print(' ok.')
                        self.ever_connected = True
                    # loop again to send
            except BaseException as e:
                if self.connected:
                    print('Disconnected. Will try to reconnect...', end='', flush=True)
                    self.connected = False
                else:
                    print('.', end='', flush=True)
                time.sleep(1)
    def close(self):
        if self.wsock is not None:
            self.wsock.close()
    def flush(self):
        # actually, we only detect errors when we read the response,
        # so we cannot just send the message here and forget it.
        # instead, we will actually do nothing here, and really send the
        # request when the calling read-eval-loop asks for the answer
        # (see the read() method above)
        pass


f = FileWSock(ws_path)
remote_api = RemoteAPIForwarder(f, json)

# read-eval-loop
code.interact(  banner='Entering interpreter prompt. Use "remote_api" variable to interact with the web api.',
                local=dict(remote_api = remote_api))
# done
f.close()
