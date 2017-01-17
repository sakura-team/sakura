#!/usr/bin/env python3

import json, code, sys, readline, os.path, atexit
sys.path.insert(0, '.')
from sakura.common.io import AttrCallAggregator
from websocket import create_connection

# Persistent command history.
histfile = os.path.join(os.environ["HOME"], ".web-api-history")
try:
    readline.read_history_file(histfile)
except IOError:
    # Existing history file can't be read.
    pass
atexit.register(readline.write_history_file, histfile)

# the real GUI sends a callback id, which is echo-ed by
# the hub together with the result.
# we do not need it here, we always set it to 0.
def get_gui_api(f, protocol):
    def remote_api_handler(path, args, kwargs):
        protocol.dump((0, path, args, kwargs), f)
        f.flush()
        return protocol.load(f)[1]
    remote_api = AttrCallAggregator(remote_api_handler)
    return remote_api

class FileWSock(object):
    def __init__(self, wsock):
        self.wsock = wsock
        self.msg = ''
    def write(self, s):
        self.msg += s
    def read(self):
        msg = self.wsock.recv()
        if msg == None:
            msg = ''
        return msg
    def flush(self):
        self.wsock.send(self.msg)
        self.msg = ''

wsock = create_connection("ws://localhost:8081/websockets/rpc")
f = FileWSock(wsock)
remote_api = get_gui_api(f, json)
# read-eval-loop
code.interact(  banner='Entering interpreter prompt. Use "remote_api" variable to interact with the web api.',
                local=dict(remote_api = remote_api))
# done
wsock.close()
