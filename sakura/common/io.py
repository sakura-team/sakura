import collections, itertools, io, sys, contextlib, traceback, builtins, numbers
import pickle, numpy as np
from threading import get_ident     # get thread id
from gevent.queue import Queue
from gevent.event import AsyncResult
from sakura.common.tools import monitored
from sakura.common.errors import APIRequestError, IOHoldException

DEBUG_LEVEL = 0   # do not print messages exchanged
#DEBUG_LEVEL = 1   # print requests and results, truncate if too verbose
#DEBUG_LEVEL = 2   # print requests and results (slowest mode)

IO_FUNC = 0
IO_ATTR = 1

IO_TRANSFERED = 0
IO_HELD = 1
IO_REQUEST_ERROR = 2
IO_STOP_ITERATION = 3

def print_debug(*args):
    if DEBUG_LEVEL == 0:
        return  # do nothing
    OUT = io.StringIO()
    print(*args, file=OUT)
    if DEBUG_LEVEL == 1 and OUT.tell() > 110:
        OUT.seek(110)
        OUT.write('...\n')
        OUT.truncate()
    sys.stdout.write(OUT.getvalue())

class HeldObjectsStore:
    instance = None
    @staticmethod
    def get():
        if HeldObjectsStore.instance is None:
            HeldObjectsStore.instance = HeldObjectsStore()
        return HeldObjectsStore.instance
    def __init__(self):
        self.__objects__ = {}
        self.__held_ids__ = itertools.count()
    def hold(self, obj):
        # hold obj locally and return its id.
        print_debug('held:', obj)
        held_id = self.__held_ids__.__next__()
        self.__objects__[held_id] = obj
        return held_id
    def __getitem__(self, held_id):
        return self.__objects__[held_id]
    def __delitem__(self, held_id):
        del self.__objects__[held_id]

# obtain a serializable description of an object
def pack(obj):
    # some classes can pass unchanged
    if isinstance(obj, str) or isinstance(obj, bytes) or \
            isinstance(obj, np.ndarray):
        return obj
    # with other objects, try to be smart
    if isinstance(obj, dict):
        return { k: pack(v) for k, v in obj.items() }
    elif isinstance(obj, type) and hasattr(obj, 'select'):    # for pony entities
        return tuple(pack(o) for o in obj.select())
    elif hasattr(obj, 'pack'):
        return pack(obj.pack())
    elif hasattr(obj, '_asdict'):
        return pack(obj._asdict())
    elif isinstance(obj, list) or isinstance(obj, tuple) or \
                hasattr(obj, '__iter__'):
        return tuple(pack(o) for o in obj)
    # object is probably a native type
    return obj

@contextlib.contextmanager
def void_context_manager():
    yield

class LocalAPIHandler(object):
    def __init__(self, f, protocol, local_api,
                greenlets_pool = None,
                session_wrapper = void_context_manager):
        self.f = f
        self.protocol = protocol
        self.api_runner = AttrCallRunner(local_api)
        self.session_wrapper = session_wrapper
        if greenlets_pool == None:
            self.pool = None
            self.handle_request = self.handle_request_base
        else:
            self.pool = greenlets_pool
            self.handle_request = self.handle_request_pool
    def loop(self):
        if self.pool is None:
            self.do_loop()
        else:
            self.handle_request_base = monitored(self.handle_request_base)
            self.pool.spawn(self.do_loop)
            self.handle_request_base.catch_issues()
    def do_loop(self):
        while True:
            should_continue = self.handle_next_request()
            if not should_continue:
                break
    def handle_next_request(self):
        try:
            req_id, req = self.protocol.load(self.f)
            print_debug('received request', str((req_id, req)))
        except BaseException:
            if DEBUG_LEVEL == 0:
                print('malformed request. closing.')
            else:
                print('malformed request? Got exception:')
                traceback.print_exc()
            return False
        self.handle_request(req_id, req)
        return True
    def handle_request_base(self, req_id, req):
        with self.session_wrapper():
            # run request
            try:
                res = self.api_runner.do(req)
                out = (IO_TRANSFERED, res)
            except StopIteration:
                out = (IO_STOP_ITERATION,)
            except APIRequestError as e:
                out = (IO_REQUEST_ERROR, str(e))
            # send response
            try:
                self.protocol.dump((req_id,) + out, self.f)
                self.f.flush()
                print_debug("sent response", (req_id,) + out)
            except IOHoldException:
                # object will be held locally
                held_id = self.api_runner.hold(res)
                origin = get_ident(), held_id
                if isinstance(res, AttrCallAggregator):
                    if res.get_origin() is not None:
                        origin = res.get_origin()
                # notify remote end
                out = (IO_HELD, held_id) + origin
                self.protocol.dump((req_id,) + out, self.f)
                self.f.flush()
            except BaseException as e:
                print('could not send response:', e)
    def handle_request_pool(self, req_id, req):
        self.pool.spawn(self.handle_request_base, req_id, req)

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
# then it is easy for api_forwarding_func to pass its arguments
# on the socket connection.
#
# on the other end, we have have a code like:
#
# api_call_runner = AttrCallRunner(api_handler)
# ...
# api_call_runner.do('my.super.function', [1, 2], {'a':3})
#
# This will cause the following to be called:
# api_handler.my.super.function(1, 2, a=3)
#
# This mechanism is efficient because it sends the whole attribute path
# at once on the network.
# However, it works with remote function calls only: api_handler.my.attr
# will not cause a request to be sent because no explicit function call
# is performed.
# If you want to make a specific attribute accessible without a function
# call, prepend a '_' to its name: for example, api_handler.my._attr
# will be recognised as a remote attribute and handled correctly.

void_result_interpreter = lambda x: x

class AttrCallAggregator(object):
    def __init__(self, request_cb, path = (),
                        origin = None,
                        delete_callback = None):
        self.path = path
        self.request = request_cb
        self.delete_callback = delete_callback
        self.__origin__ = origin
    def __getattr__(self, attr):
        path = self.path + (attr,)
        if attr.startswith('_'):
            return self.__io_request__(IO_ATTR, path)
        else:
            return AttrCallAggregator(self.request, path, self.__origin__)
    def __str__(self):
        path = self.path + ('__str__',)
        return 'REMOTE(' + self.__io_request__(IO_FUNC, path, (), {}) + ')'
    def __repr__(self):
        path = self.path + ('__repr__',)
        return 'REMOTE(' + self.__io_request__(IO_FUNC, path, (), {}) + ')'
    def __iter__(self):
        path = self.path + ('__iter__',)
        return self.__io_request__(IO_FUNC, path, (), {})
    def __next__(self):
        path = self.path + ('__next__',)
        return self.__io_request__(IO_FUNC, path, (), {})
    def __delete_held__(self, remote_held_id):
        self.request(IO_FUNC, ('__delete_held__',), (remote_held_id,), {})
    def __getitem__(self, index):
        return AttrCallAggregator(self.request, self.path + ((index,),), self.__origin__)
    def __call__(self, *args, **kwargs):
        return self.__io_request__(IO_FUNC, self.path, args, kwargs)
    def __len__(self):
        path = self.path + ('__len__',)
        return self.__io_request__(IO_FUNC, path, (), {})
    def get_origin(self):
        return self.__origin__
    def __del__(self):
        if self.delete_callback is not None:
            self.delete_callback()
    def __io_request__(self, *req):
        res = self.request(*req)
        if res[0] == IO_TRANSFERED:
            # result was transfered, return it
            return res[1]
        if res[0] == IO_STOP_ITERATION:
            raise StopIteration
        if res[0] == IO_REQUEST_ERROR:
            raise APIRequestError(res[1])
        if res[0] == IO_HELD:
            # result was held remotely (not transferable)
            remote_held_id, origin = res[1], res[2:]
            origin_tid, origin_held_id = origin
            if origin_tid == get_ident():
                # the object is actually a local object!
                # (may occur in case of several bounces)
                # we can short out those bounces and use the object directly.
                # first, retrieve a reference to this object
                obj = HeldObjectsStore.get()[origin_held_id]
                # tell the remote end it can release it
                self.__delete_held__(remote_held_id)
                # return the object
                return obj
            remote_held_path = ('__held_objects__', (remote_held_id,))
            return AttrCallAggregator(self.request, remote_held_path, origin,
                    delete_callback=lambda : self.__delete_held__(remote_held_id))

class AttrCallRunner(object):
    def __init__(self, handler):
        self.handler = handler
        self.__held_objects__ = HeldObjectsStore.get()
    def hold(self, obj):
        return self.__held_objects__.hold(obj)
    def do(self, req):
        req_type, path = req[:2]
        if path[0] in ('__held_objects__', '__delete_held__'):
            # management of held objects
            obj = self
        else:
            obj = self.handler
        for attr in path:
            if isinstance(attr, str):
                obj = getattr(obj, attr)
            else:
                obj = obj[attr[0]]  # getitem
        if req_type == IO_ATTR:
            return obj
        elif req_type == IO_FUNC:
            args, kwargs = req[2:4]
            return obj(*args, **kwargs)
    def __delete_held__(self, held_id):
        del self.__held_objects__[held_id]

class RemoteAPIForwarder(AttrCallAggregator):
    def __init__(self, f, protocol):
        super().__init__(self.request)
        self.f = f
        self.protocol = protocol
        self.reqs = {}
        self.req_ids = itertools.count()
        self.running = False
    def request(self, *req):
        req_id = self.req_ids.__next__()
        async_res = AsyncResult()
        self.reqs[req_id] = async_res
        print_debug("sent request", req_id, req)
        self.protocol.dump((req_id, req), self.f)
        self.f.flush()
        # if the greenlet did not start the loop() method,
        # block until we get the result. (initialization phase)
        if not self.running:
            self.receive()
        return async_res.get()
    def receive(self):
        try:
            res_info = self.protocol.load(self.f)
            print_debug("received response", res_info)
        except BaseException:
            if DEBUG_LEVEL == 0:
                print('malformed result. closing.')
            else:
                print('malformed result? Got exception:')
                traceback.print_exc()
            return False
        req_id = res_info[0]
        async_res = self.reqs[req_id]
        async_res.set(res_info[1:])
        del self.reqs[req_id]
        return True
    def loop(self):
        self.running = True
        while self.receive():
            pass

IO_TRANSFERABLES = (None.__class__, np.ndarray, numbers.Number, np.dtype) + \
                   tuple(getattr(builtins, t) for t in ( \
                        'bytearray', 'bytes', 'dict', 'frozenset', 'list',
                        'set', 'str', 'tuple', 'BaseException', 'type'))

class PickleLocalAPIProtocol:
    @staticmethod
    def load(f):
        return pickle.load(f)
    @staticmethod
    def dump(res_info, f):
        if res_info[1] == IO_TRANSFERED and \
                not isinstance(res_info[2], IO_TRANSFERABLES):
            # res probably should not be serialized,
            # hold it locally.
            raise IOHoldException
        return pickle.dump(res_info, f)
