import ssl, time, gevent
from sakura.common.tools import ObservableEvent
from websocket import create_connection
from sakura.client import conf
from sakura.client.apiobject.root import APIRoot
from gevent.socket import wait_read, wait_write
from gevent.lock import BoundedSemaphore

class FileWSock(object):
    def __init__(self):
        self.ever_connected = False
        self.wsock = None
    def connect(self):
        try:
            self.connect_with_url(get_ws_url(conf.hub_host, conf.hub_port, ssl = True))
            return True
        except ssl.SSLError:
            self.connect_with_url(get_ws_url(conf.hub_host, conf.hub_port, ssl = False))
            return False
    def connect_with_url(self, url):
        self.wsock = create_connection(url)
        self.ever_connected = True
    def write(self, s):
        wsock = self.wsock
        try:
            wait_write(wsock.fileno())
            return wsock.send(s)
        except:
            if wsock.connected:
                wsock.close()
            raise
    def read(self):
        wsock = self.wsock
        try:
            wait_read(wsock.fileno())
            msg = wsock.recv()
            if msg == None:
                msg = ''
            return msg
        except:
            if wsock.connected:
                wsock.close()
            raise
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
                            ssl = self.ws.connect()
                            if ever_connected:
                                self.connecting_message.print('... OK, repaired.', end='')
                            else:
                                self.connecting_message.print('... OK.', end='')
                            if ssl:
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

def get_ws_url(hub_host, hub_port, ssl):
    if ssl:
        protocol = 'wss'
    else:
        protocol = 'ws'
    return "%s://%s:%d/websocket" % (protocol, hub_host, hub_port)

def get_api():
    ws = WSProxy(FileWSock())
    return APIRoot(ws)

