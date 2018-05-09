import collections, itertools, io, sys, contextlib, traceback, builtins, numbers
import numpy as np
from gevent.queue import Queue
from gevent.event import AsyncResult
from sakura.common.tools import monitored

DEBUG_LEVEL = 0   # do not print messages exchanged
#DEBUG_LEVEL = 1   # print requests and results, truncate if too verbose
#DEBUG_LEVEL = 2   # print requests and results (slowest mode)

IO_FUNC = 0
IO_ATTR = 1

IO_TRANSFERED = 0
IO_HELD = 1

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

@contextlib.contextmanager
def void_context_manager():
    yield

class VoidResultWrapper:
    @staticmethod
    def on_success(result):
        return result
    @staticmethod
    def on_exception(exc):
        raise exc

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

class LocalAPIHandler(object):
    def __init__(self, f, protocol, local_api,
                greenlets_pool = None,
                session_wrapper = void_context_manager,
                result_wrapper = VoidResultWrapper):
        self.f = f
        self.protocol = protocol
        self.api_runner = AttrCallRunner(local_api, result_wrapper)
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
            res = self.api_runner.do(req)
            try:
                #expanded_res = make_serializable(res)
                self.protocol.dump((req_id, res), self.f)
                print_debug("sent response", req_id, res)
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

class AttrCallAggregator(object):
    def __init__(self, request_cb, path = (), delete_callback = None):
        self.path = path
        self.request = request_cb
        self.delete_callback = delete_callback
    def __getattr__(self, attr):
        path = self.path + (attr,)
        if attr.startswith('_'):
            return self.__io_request__(IO_ATTR, path)
        else:
            return AttrCallAggregator(self.request, path)
    def __str__(self):
        path = self.path + ('__str__',)
        return 'REMOTE(' + self.__io_request__(IO_FUNC, path, (), {})[1] + ')'
    def __repr__(self):
        path = self.path + ('__repr__',)
        return 'REMOTE(' + self.__io_request__(IO_FUNC, path, (), {})[1] + ')'
    def __iter__(self):
        path = self.path + ('__iter__',)
        return self.__io_request__(IO_FUNC, path, (), {})
    def __next__(self):
        path = self.path + ('__next__',)
        return self.__io_request__(IO_FUNC, path, (), {})
    def __delete_held__(self, remote_held_id):
        self.request(IO_FUNC, ('__delete_held__',), (remote_held_id,), {})
    def __getitem__(self, index):
        return AttrCallAggregator(self.request, self.path + ((index,),))
    def __call__(self, *args, **kwargs):
        return self.__io_request__(IO_FUNC, self.path, args, kwargs)
    def __len__(self):
        path = self.path + ('__len__',)
        return self.__io_request__(IO_FUNC, path, (), {})
    def __del__(self):
        if self.delete_callback is not None:
            self.delete_callback()
    def __io_request__(self, *req):
        res = self.request(*req)
        if res == StopIteration:
            raise StopIteration
        if res[0] == IO_TRANSFERED:
            # result was transfered, return it
            return res[1]
        else:      # IO_HELD
            # result was held remotely (not transferable)
            remote_held_id = res[1]
            remote_held_path = ('__held_objects__', (remote_held_id,))
            return AttrCallAggregator(self.request, remote_held_path,
                    delete_callback=lambda : self.__delete_held__(remote_held_id))

IO_TRANSFERABLES = (None.__class__, np.ndarray, numbers.Number, np.dtype) + \
                   tuple(getattr(builtins, t) for t in ( \
                        'bytearray', 'bytes', 'dict', 'frozenset', 'list',
                        'set', 'str', 'tuple', 'BaseException', 'type'))

class AttrCallRunner(object):
    def __init__(self, handler, result_wrapper):
        self.handler = handler
        self.__held_ids__ = itertools.count()
        self.__held_objects__ = {}
        self.result_wrapper = result_wrapper
    def do(self, req):
        try:
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
                res = obj
            elif req_type == IO_FUNC:
                args, kwargs = req[2:4]
                res = obj(*args, **kwargs)
            res = self.result_wrapper.on_success(res)
        except StopIteration:
            return StopIteration
        except BaseException as e:
            print(e)
            res = self.result_wrapper.on_exception(e)
        if isinstance(res, IO_TRANSFERABLES):
            return IO_TRANSFERED, res
        else:
            # res probably cannot be serialized,
            # hold it locally and return its id.
            print_debug('held:', res)
            held_id = self.__held_ids__.__next__()
            self.__held_objects__[held_id] = res
            return IO_HELD, held_id
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
            req_id, res = self.protocol.load(self.f)
            print_debug("received response", req_id, res)
        except BaseException:
            if DEBUG_LEVEL == 0:
                print('malformed result. closing.')
            else:
                print('malformed result? Got exception:')
                traceback.print_exc()
            return False
        async_res = self.reqs[req_id]
        async_res.set(res)
        del self.reqs[req_id]
        return True
    def loop(self):
        self.running = True
        while self.receive():
            pass

