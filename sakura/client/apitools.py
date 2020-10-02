import ssl, time, gevent
from gevent import Greenlet
from gevent.socket import wait_read, wait_write
from gevent.queue import Queue
from websocket import create_connection
from sakura.client import conf
from sakura.client.apiobject.root import APIRoot
from sakura.common.io.serializer import Serializer
from sakura.common.io import APIEndpoint
from sakura.common.tools import WSOCK_PICKLE, JSON_PROTOCOL
from sakura.common.errors import IOReadException, IOWriteException

DEBUG=False
PROTOCOLS = { 'json': JSON_PROTOCOL,
              'pickle': WSOCK_PICKLE }
PROTO_NAME = 'pickle'

def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

# add wait_read & wait_write to make websocket cooperate in a gevent context
class GeventWSock(object):
    def __init__(self, wsock):
        self.wsock = wsock
    def send(self, s):
        try:
            wait_write(self.wsock.fileno())
            debug_print('writing', s, '... ', end='')
            num = self.wsock.send(s)
            debug_print('OK')
            return num
        except:
            debug_print('exception!')
            raise IOWriteException("Could not write websocket message.")
    def recv(self):
        try:
            wait_read(self.wsock.fileno())
            debug_print('reading... ', end='')
            msg = self.wsock.recv()
            if len(msg) > 40:
                debug_print('OK', msg[:37] + '...')
            else:
                debug_print('OK', msg)
            return msg
        except:
            debug_print('exception!')
            raise IOReadException("Could not read websocket message.")
    def close(self):
        self.wsock.close()
    @property
    def connected(self):
        return self.wsock.connected
    def fileno(self):
        return self.wsock.fileno()

class LoginException(Exception):
    pass

class GeventWSockConnector(object):
    def __init__(self):
        self.ever_connected = False
        self.wsock = None
    def connect(self):
        web_protocol, hub_host = conf.hub_url.rstrip('/').split('://')
        protocol = web_protocol.replace('http', 'ws')
        url = "%s://%s/api-websocket?protocol=%s" % (protocol, hub_host, PROTO_NAME)
        self.wsock = Serializer(GeventWSock(create_connection(url)))
        self.login()
        self.ever_connected = True
    def login(self):
        if conf.username is None:
            self.wsock.send('Anonymous')
        else:
            self.wsock.send('Login')
            self.wsock.send(conf.username)
            self.wsock.send(conf.password_hash)
        resp = self.wsock.recv()
        if resp != 'OK':
            raise LoginException('Failed login')
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
        if self.closed:
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

# On 4th connection attempt, start to inform the user why this is taking time.
# Otherwise, work silently.
RECONNECTION_WARNING_TRESHOLD=4

class WSManager:
    def __init__(self, ws):
        self.ws = ws
        self.connecting_message = ProgressMessage()
        self.connect_timeout = None
        self.connect_attempt = 0
        self.endpoint = APIEndpoint(self, PROTOCOLS[PROTO_NAME], None)
        self.endpoint_greenlet = None
        self.proxy = self.endpoint.proxy
        self.waiting_greenlets = {}
    @property
    def connecting(self):
        return self.connect_attempt > 0
    def set_connect_timeout(self, value):
        self.connect_timeout = value
    def write(self, s):
        if len(s) == 0:
            return 0
        return self.loop_io_do(True, self.ws.write, s)
    def read(self):
        return self.loop_io_do(False, self.ws.read)
    def check_connect(self, can_reconnect):
        if self.ws.connected:
            return # nothing to do
        if not self.connecting and can_reconnect:
            self.connect_attempt = 1
            self.do_connect()
            # unblock waiting greenlets
            queues = self.waiting_greenlets.values()
            self.waiting_greenlets = {}
            for q in queues:
                q.put(1)
            self.connect_attempt = 0
            return
        # otherwise, wait for notification from reconnection greenlet
        # when we will be connected.
        curr_greenlet = gevent.getcurrent()
        if curr_greenlet not in self.waiting_greenlets:
            self.waiting_greenlets[curr_greenlet] = Queue()
        queue = self.waiting_greenlets[curr_greenlet]
        queue.get()
        return
    def silent_endpoint_loop(self):
        try:
            self.endpoint.loop()
        except:
            pass    # just exit silently
    def do_connect(self):
        while True:
            try:
                ever_connected = self.ws.ever_connected
                # if connection / reconnection works on one of the first attempts, do not bother the user
                # with explanations.
                if self.connect_attempt == RECONNECTION_WARNING_TRESHOLD:
                    if ever_connected:
                        self.connecting_message.init('Disconnected. Trying to reconnect...', end='')
                    else:
                        self.connecting_message.init('Connecting...', end='')
                self.ws.connect()
                self.endpoint_greenlet = Greenlet.spawn(self.silent_endpoint_loop)
                if DEBUG:
                    import random
                    self.endpoint_greenlet.name = 'api-endpoint-loop-' + str(random.randint(0, 1000))
                    debug_print('spawned greenlet ' + self.endpoint_greenlet.name)
                if self.connect_attempt >= RECONNECTION_WARNING_TRESHOLD:
                    if ever_connected:
                        self.connecting_message.print('... OK, repaired.')
                    else:
                        self.connecting_message.print('... OK.')
                return
            except LoginException as e:
                self.connecting_message.print('... FAILED.')
                raise
            except BaseException as e:
                debug_print(e)
                pass    # handle below
            # handle exception
            if self.connect_timeout is None or self.connect_attempt < self.connect_timeout:
                if self.connect_attempt >= RECONNECTION_WARNING_TRESHOLD:
                    self.connecting_message.print('.', end='')
                self.connect_attempt += 1
                time.sleep(1)
                continue
            else:
                if self.connect_attempt >= RECONNECTION_WARNING_TRESHOLD:
                    self.connecting_message.print('... FAILED.')
                raise TimeoutError

    def loop_io_do(self, can_reconnect, func, *args):
        while True:
            self.check_connect(can_reconnect)
            try:
                res = func(*args)
                return res
            except BaseException as e:
                debug_print(e)
                if self.endpoint_greenlet is not None:
                    debug_print(gevent.getcurrent(), '-- killing greenlet ' + self.endpoint_greenlet.name)
                    g = self.endpoint_greenlet
                    self.endpoint_greenlet = None
                    g.kill()

    def close(self):
        if self.endpoint_greenlet is not None:
            self.endpoint_greenlet.kill()
            self.endpoint_greenlet = None
        if not self.ws.closed:
            self.ws.close()
    @property
    def closed(self):
        return self.ws.closed
    def flush(self):
        self.ws.flush()
    def fileno(self):
        return self.ws.fileno()


def get_api():
    ws = WSManager(GeventWSockConnector())
    return APIRoot(ws)
