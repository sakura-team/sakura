#!/usr/bin/env python3

import ssl, json, time, contextlib, pathlib
from sakura.common.io import RemoteAPIForwarder
from websocket import create_connection
from sakura.client.apiobject.root import APIRoot

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
        self.ever_connected = True
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
                    ever_connected = self.ever_connected
                    self.connect()
                    if ever_connected:
                        print(' ok, repaired.')
                    else:
                        print(' ok.')
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

def get_api_for_url(ws_url):
    ws = FileWSock(ws_url)
    ws.connect()
    remote_api = RemoteAPIForwarder(ws, json, sync=True)
    return APIRoot(remote_api, ws)

def get_conf():
    conf_path = pathlib.Path.home() / '.sakura' / 'client.conf'
    if not conf_path.exists():
        conf = dict(
            hub_host = input('Enter sakura-hub ip or hostname: '),
            hub_port = int(input('Enter sakura-hub websocket port: '))
        )
        conf_path.parent.mkdir(parents=True, exist_ok=True)
        conf_path.write_text(json.dumps(conf))
        print('Config saved at ' + str(conf_path))
    else:
        print('Reading sakura client conf from ' + str(conf_path))
        conf = json.loads(conf_path.read_text())
    return conf

def get_ws_url(hub_host, hub_port, ssl):
    if ssl:
        protocol = 'wss'
    else:
        protocol = 'ws'
    return "%s://%s:%d/websocket" % (protocol, hub_host, hub_port)

def get_api():
    conf = get_conf()
    try:
        return get_api_for_url(get_ws_url(ssl = True, **conf))
    except ssl.SSLError:
        print('WARNING: SSL-handshake failed. Setting up a clear text connection!')
        return get_api_for_url(get_ws_url(ssl = False, **conf))

@contextlib.contextmanager
def connect_to_hub():
    remote_api = get_api()
    yield remote_api
    remote_api._close()

