import collections, itertools
from gevent.queue import Queue
from gevent.event import AsyncResult

ParsedRequest = collections.namedtuple('ParsedRequest',
                    ('req_id', 'path', 'args', 'kwargs'))

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
            raw_req = self.protocol.load(self.f)
            req = ParsedRequest(*raw_req)
            print('received', req)
        except BaseException:
            print('malformed request. closing.')
            return False
        res = self.api_runner.do(
            req.path, req.args, req.kwargs)
        try:
            self.protocol.dump((req.req_id, res), self.f)
            print("sent",res)
            self.f.flush()
        except BaseException:
            print('could not send response. closing.')
            return False
        return True

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
    def __getitem__(self, index):
        return AttrCallAggregator(self.handler, self.path + ((index,),))
    def __call__(self, *args, **kwargs):
        return self.handler(self.path, args, kwargs)

class AttrCallRunner(object):
    def __init__(self, handler):
        self.handler = handler
    def do(self, path, args, kwargs):
        obj = self.handler
        for attr in path:
            if isinstance(attr, str):
                obj = getattr(obj, attr)
            else:
                obj = obj[attr[0]]  # getitem
        return obj(*args, **kwargs)

class RemoteAPIForwarder(AttrCallAggregator):
    def __init__(self, f, protocol):
        super().__init__(self.handler)
        self.f = f
        self.protocol = protocol
        self.reqs = {}
        self.req_ids = itertools.count()
        self.running = False
    def handler(self, path, args, kwargs):
        req_id = self.req_ids.__next__()
        async_res = AsyncResult()
        self.reqs[req_id] = async_res
        self.protocol.dump((req_id, path, args, kwargs), self.f)
        self.f.flush()
        # if the greenlet did not start the loop() method,
        # block until we get the result. (initialization phase)
        if not self.running:
            self.next_result()
        return async_res.get()
    def next_result(self):
        req_id, res = self.protocol.load(self.f)
        async_res = self.reqs[req_id]
        async_res.set(res)
        del self.reqs[req_id]
    def loop(self):
        self.running = True
        while True:
            self.next_result()

