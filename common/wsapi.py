import collections
from geventwebsocket import WebSocketError
from websocket import create_connection

def get_remote_api(wsock, protocol):
    def remote_api_handler(path, args, kwargs):
        msg = protocol.dumps((path, args, kwargs))
        wsock.send(msg)
        res = wsock.recv()
        return protocol.loads(res)
    remote_api = AttrCallAggregator(remote_api_handler)
    return remote_api

ParsedRequest = collections.namedtuple('ParsedRequest',
                    ('path', 'args', 'kwargs'))

class LocalAPIHandler(object):
    def __init__(self, wsock, protocol, local_api):
        self.wsock = wsock
        self.protocol = protocol
        self.api_runner = AttrCallRunner(local_api)
    def loop(self):
        while True:
            should_continue = self.handle_next_request()
            if not should_continue:
                break
    def handle_next_request(self):
        try:
            req = self.wsock.receive()
            if req == None:
                return False
            parsed = self.parse_request(req)
            res = self.api_runner.do(
                parsed.path, parsed.args, parsed.kwargs)
            res = self.format_result(parsed, res)
            self.wsock.send(res)
        except WebSocketError:
            return False
        return True
    def parse_request(self, req):
        return ParsedRequest(*self.protocol.loads(req))
    def format_result(self, parsed_request, res):
        return self.protocol.dumps(res)

def get_client_wsock(url):
    wsock = create_connection(url)
    # server side is implemented using gevent.geventwebsocket
    # client side is implemented using [stdlib].websocket
    # the recv methods do not have the same name, let's fix that
    wsock.receive = wsock.recv
    return wsock

# The following pair of classes allows to pass API calls efficiently
# over a network socket.
#
# On the emitter end, we will have the following kind of code:
#
# api = AttrCallAggregator(api_forwarding_func)
# ...
# res = api.my.super.function(1, 2, a=3)
#
# This will cause the following to be called:
# api_forwarding_func('my.super.function', [1, 2], {'a':3})
#
# then it is easy for api_backend_func to pass its arguments
# on the socket connection.
#
# on the other end, we have have a code like:
#
# api_call_runner = AttrCallRunner(api_handler)
# ...
# api_call_runner.do('my.super.function', [1, 2], {'a':3})
#
# This will call the following to be called:
# api_handler.my.super.function(1, 2, a=3)
#
# This mechanism is efficient because it sends the whole attribute path
# at once on the network.
# Drawback: It works with remote function calls only, i.e. all
# remote attributes accessed must be functions.

class AttrCallAggregator(object):
    def __init__(self, handler, path = ()):
        self.path = path
        self.handler = handler
    def __getattr__(self, attr):
        return AttrCallAggregator(self.handler, self.path + (attr,))
    def __call__(self, *args, **kwargs):
        path = '.'.join(self.path)
        return self.handler(path, args, kwargs)

class AttrCallRunner(object):
    def __init__(self, handler):
        self.handler = handler
    def do(self, path, args, kwargs):
        obj = self.handler
        for attr in path.split('.'):
            obj = getattr(obj, attr)
        return obj(*args, **kwargs)

