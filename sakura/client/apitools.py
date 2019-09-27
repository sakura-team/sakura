import ssl, time, gevent
from sakura.common.tools import ObservableEvent
from websocket import create_connection
from sakura.client import conf
from sakura.client.apiobject.root import APIRoot
from gevent.socket import wait_read, wait_write
from gevent.lock import BoundedSemaphore
from sakura.common.io.serializer import Serializer

# add wait_read & wait_write to make websocket cooperate in a gevent context
class GeventWSock(object):
    def __init__(self, wsock):
        self.wsock = wsock
    def send(self, s):
        wait_write(self.wsock.fileno())
        return self.wsock.send(s)
    def recv(self):
        wait_read(self.wsock.fileno())
        return self.wsock.recv()
    def close(self):
        self.wsock.close()
    @property
    def connected(self):
        return self.wsock.connected
    def fileno(self):
        return self.wsock.fileno()

class GeventWSockConnector(object):
    def __init__(self):
        self.ever_connected = False
        self.wsock = None
    def connect(self):
        try:
            self.wsock = self.connect_with_url(get_ws_url(conf.hub_host, conf.hub_port, ssl_enabled = True))
            ssl_enabled = True
        except ssl.SSLError:
            self.wsock = self.connect_with_url(get_ws_url(conf.hub_host, conf.hub_port, ssl_enabled = False))
            ssl_enabled = False
        self.ever_connected = True
        return ssl_enabled
    def connect_with_url(self, url):
        return Serializer(GeventWSock(create_connection(url)))
    def write(self, s):
        return self.wsock.send(s)
    def read(self):
        return self.wsock.recv()
    def close(self):
        if not self.closed:
            self.wsock.close()
    @property
    def closed(self):
        return self.wsock is None or not self.wsock.connected
    def flush(self):
        pass
    @property
    def connected(self):
        return not self.closed
    def fileno(self):
        if self.wsock is None:
            return None
        return self.wsock.fileno()

class ProgressMessage:
    def __init__(self):
        self.line_size = 0
    def init(self, s, end='\n'):
        self.line_size = 0
        self.print(s, end)
    def print(self, s, end='\n'):
        if len(s.rstrip()) + self.line_size > 100:
            print()
            self.line_size = 0
            s = s.lstrip()
        print(s, end=end, flush=True)
        if end == '\n':
            self.line_size = 0
        else:
            self.line_size += len(s)

class WSProxy:
    def __init__(self, ws):
        self.auto_reconnect = False
        self.ws = ws
        self.on_connect = ObservableEvent()
        self.on_disconnect = ObservableEvent()
        self.connect_semaphore = BoundedSemaphore()
        self.connecting = False
        self.connecting_message = ProgressMessage()
    def set_auto_reconnect(self, value):
        self.auto_reconnect = value
    def write(self, s):
        if len(s) == 0:
            return 0
        return self.loop_io_do(True, self.ws.write, s)
    def read(self):
        return self.loop_io_do(False, self.ws.read)
    def loop_io_do(self, can_reconnect, func, *args):
        if not self.ws.ever_connected:
            self.connecting_message.init('Connecting...', end='')
            self.connecting = True
        while True:
            try:
                if self.ws.connected:
                    res = func(*args)
                    return res
                else:
                    with self.connect_semaphore:
                        if not self.ws.connected and can_reconnect:
                            ever_connected = self.ws.ever_connected
                            ssl_enabled = self.ws.connect()
                            if ever_connected:
                                self.connecting_message.print('... OK, repaired.', end='')
                            else:
                                self.connecting_message.print('... OK.', end='')
                            if ssl_enabled:
                                self.connecting_message.print()     # all is fine
                            else:
                                self.connecting_message.print(' WARNING: SSL-handshake failed. A clear text connection was set up!')
                            self.on_connect.notify()
                            self.connecting = False
                    gevent.idle()
                    continue
            except BaseException as e:
                pass    # handle below
            # handle exception
            if self.connecting:
                self.connecting_message.print('.', end='')
                time.sleep(1)
                continue
            with self.connect_semaphore:
                if not self.ws.connected and can_reconnect:
                    if self.ws.ever_connected:
                        self.on_disconnect.notify()
                        if self.auto_reconnect:
                            self.connecting_message.init('Disconnected. Trying to reconnect...', end='')
                            self.connecting = True
                        else:
                            raise ConnectionResetError('Connection to hub was lost!')
    def close(self):
        self.ws.close()
    @property
    def closed(self):
        return self.ws.closed
    def flush(self):
        self.ws.flush()
    def fileno(self):
        return self.ws.fileno()

def get_ws_url(hub_host, hub_port, ssl_enabled):
    if ssl_enabled:
        protocol = 'wss'
    else:
        protocol = 'ws'
    return "%s://%s:%d/websocket" % (protocol, hub_host, hub_port)

def get_api():
    ws = WSProxy(GeventWSockConnector())
    return APIRoot(ws)

