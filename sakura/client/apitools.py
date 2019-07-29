import ssl, json, time, contextlib, pathlib
from sakura.common.tools import JSON_PROTOCOL
from sakura.common.io import APIEndpoint
from websocket import create_connection
from sakura.client.apiobject.root import APIRoot
from gevent.socket import wait_read, wait_write

class FileWSock(object):
    def __init__(self):
        self.conf = None
        self.connected = False
        self.ever_connected = False
        self.wsock = None
    def connect(self):
        if self.conf is None:
            self.conf = get_conf()
        try:
            self.connect_with_url(get_ws_url(ssl = True, **self.conf))
        except ssl.SSLError:
            print('WARNING: SSL-handshake failed. Setting up a clear text connection!')
            self.connect_with_url(get_ws_url(ssl = False, **self.conf))
    def connect_with_url(self, url):
        self.wsock = create_connection(url)
        self.connected = True
        self.ever_connected = True
    def write(self, s):
        if len(s) == 0:
            return 0
        return self.loop_io_do(self.raw_write, s)
    def raw_write(self, s):
        wait_write(self.wsock.fileno())
        self.wsock.send(s)
    def read(self):
        return self.loop_io_do(self.raw_read)
    def raw_read(self):
        wait_read(self.wsock.fileno())
        msg = self.wsock.recv()
        if msg == None:
            msg = ''
        return msg
    def loop_io_do(self, func, *args):
        if not self.ever_connected:
            print('Connecting...', end='', flush=True)
        while True:
            try:
                if self.connected:
                    return func(*args)
                else:
                    ever_connected = self.ever_connected
                    self.connect()
                    if ever_connected:
                        print(' ok, repaired.')
                    else:
                        print(' ok.')
                    # loop again
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
    @property
    def closed(self):
        return self.wsock is None or not self.wsock.connected
    def flush(self):
        pass

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
    ws = FileWSock()
    endpoint = APIEndpoint(ws, JSON_PROTOCOL, None)
    return APIRoot(endpoint, ws)

@contextlib.contextmanager
def connect_to_hub():
    remote_api = get_api()
    yield remote_api
    remote_api._close()

