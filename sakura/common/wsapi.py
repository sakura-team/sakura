import collections
from geventwebsocket import WebSocketError
from websocket import create_connection

def get_remote_api(f, protocol):
    def remote_api_handler(path, args, kwargs):
        protocol.dump((path, args, kwargs), f)
        f.flush()
        return protocol.load(f)
    remote_api = AttrCallAggregator(remote_api_handler)
    return remote_api

ParsedRequest = collections.namedtuple('ParsedRequest',
                    ('path', 'args', 'kwargs'))

class LocalAPIHandler(object):
    def __init__(self, f, protocol, local_api):
        self.f = f
        self.protocol = protocol
        self.api_runner = AttrCallRunner(local_api)
    def loop(self):
        while True:
            should_continue = self.handle_next_request()
            if not should_continue:
                break
    def handle_next_request(self):
        try:
            req = self.receive_request()
            print('received',req)
            if req == None:
                return False
            res = self.api_runner.do(
                req.path, req.args, req.kwargs)
            self.send_result(req, res)
            print("sent",res)
            self.f.flush()
        except BaseException:
            return False
        return True
    def receive_request(self):
        raw_req = self.protocol.load(self.f)
        if raw_req == None:
            return None
        return ParsedRequest(*raw_req)
    def send_result(self, req, res):
        self.protocol.dump(res, self.f)

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

