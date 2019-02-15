import collections, itertools, io, sys, traceback, builtins
import gevent.pool
from os import getpid
from gevent.queue import Queue
from gevent.event import AsyncResult
from sakura.common.tools import monitored, ObservableEvent
from sakura.common.errors import APIReturningError, APIRemoteError, \
                                 IOHoldException, APIInvalidRequest
from sakura.common import errors
from sakura.common.io.debug import print_debug
from sakura.common.io.held import HeldObjectsStore
from sakura.common.io.tools import void_context_manager
from sakura.common.io.const import IO_FUNC, IO_ATTR, \
            IO_TRANSFERED, IO_HELD, IO_REQUEST_ERROR, IO_STOP_ITERATION

class LocalAPIHandler(object):
    def __init__(self, f, protocol, local_api,
                session_wrapper = void_context_manager):
        self.f = f
        self.protocol = protocol
        self.api_runner = AttrCallRunner(local_api)
        self.session_wrapper = session_wrapper
        self.pool = gevent.pool.Group()
        # redirect exceptions of all sub-greenlets to the same queue
        self.do_loop = monitored(self.do_loop)
        self.handle_request_base = monitored(
                self.handle_request_base, self.do_loop.out_queue)
    def loop(self):
        try:
            # start
            self.pool.spawn(self.do_loop)
            # wait for an exception
            self.do_loop.catch_issues()
        except (EOFError, ConnectionResetError):
            return  # leave the loop
    def do_loop(self):
        while True:
            should_continue = self.handle_next_request()
            if not should_continue:
                break
    def handle_next_request(self):
        try:
            req_id, req = self.protocol.load(self.f)
            print_debug('received request', str((req_id, req)))
        except (EOFError, ConnectionResetError):
            print('remote end disconnected!')
            raise   # we should stop
        except APIInvalidRequest:
            print('malformed request.')
            return False
        except BaseException:
            print('malformed request? Got exception:')
            traceback.print_exc()
            return False
        self.pool.spawn(self.handle_request_base, req_id, req)
        return True
    def handle_request_base(self, req_id, req):
        with self.session_wrapper():
            # run request
            try:
                res = self.api_runner.do(req)
                out = (IO_TRANSFERED, res)
            except StopIteration:
                out = (IO_STOP_ITERATION,)
            except BaseException as e:
                data = getattr(e, 'data', {})
                out = (IO_REQUEST_ERROR, e.__class__.__name__, str(e), data)
            # send response
            try:
                self.protocol.dump((req_id,) + out, self.f)
                self.f.flush()
                print_debug("sent response", (req_id,) + out)
            except IOHoldException:
                # object will be held locally
                held_id = self.api_runner.hold(res)
                origin = getpid(), held_id
                if isinstance(res, AttrCallAggregator):
                    if res.get_origin() is not None:
                        origin = res.get_origin()
                # notify remote end
                out = (IO_HELD, held_id) + origin
                self.protocol.dump((req_id,) + out, self.f)
                self.f.flush()
                sys.last_traceback = None   # let garbage collector work
            except BaseException as e:
                print('could not send response:', e)

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
    def __init__(self, top_level_api, path = (),
                        origin = None,
                        delete_callback = None):
        self.path = path
        self.top_level_api = top_level_api
        self.request = top_level_api.request
        self.delete_callback = delete_callback
        self.__origin__ = origin
    def __getattr__(self, attr):
        path = self.path + (attr,)
        if attr.startswith('_'):
            return self.__io_request__(IO_ATTR, path)
        else:
            return AttrCallAggregator(self.top_level_api, path, self.__origin__)
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
        return AttrCallAggregator(self.top_level_api, self.path + ((index,),), self.__origin__)
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
            cls_name, msg, data = res[1:]
            cls = getattr(errors, cls_name, None)
            if cls is None: cls = getattr(builtins, cls_name, None)
            if cls is None: cls = APIReturningError
            exc = cls(msg)
            exc.data = data
            self.top_level_api.on_remote_exception.notify(exc)
            raise exc
        if res[0] == IO_HELD:
            # result was held remotely (not transferable)
            remote_held_id, origin = res[1], res[2:]
            origin_pid, origin_held_id = origin
            if origin_pid == getpid():
                # the object is actually a local object!
                # (may occur in case of several bounces)
                # we can short out those bounces and use the object directly.
                # first, retrieve a reference to this object
                obj = HeldObjectsStore.get()[origin_held_id]
                print_debug('shortcut:', obj, 'is actually local.')
                # tell the remote end it can release it
                self.__delete_held__(remote_held_id)
                # return the object
                return obj
            remote_held_path = ('__held_objects__', (remote_held_id,))
            return AttrCallAggregator(self.top_level_api, remote_held_path, origin,
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
        try:
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
        except AttributeError as e:
            raise APIInvalidRequest(str(e))
    def __delete_held__(self, held_id):
        del self.__held_objects__[held_id]

class RemoteAPIForwarder(AttrCallAggregator):
    def __init__(self, f, protocol, sync=False):
        super().__init__(self)
        self.f = f
        self.protocol = protocol
        self.reqs = {}
        self.req_ids = itertools.count()
        self.sync = sync
        self.on_remote_exception = ObservableEvent()
    def request(self, *req):
        req_id = self.req_ids.__next__()
        async_res = AsyncResult()
        self.reqs[req_id] = async_res
        print_debug("sent request", req_id, req)
        self.protocol.dump((req_id, req), self.f)
        self.f.flush()
        # synchronous mode, for web api
        if self.sync:
            self.receive()
        res = async_res.get()
        if isinstance(res, BaseException):
            raise APIRemoteError(str(res))
        return res
    def handle_receive_exception(self, e):
        # connection issue, pass exception to all
        # awaiting requests
        for async_res in self.reqs.values():
            async_res.set(e)
        return False
    def receive(self):
        try:
            res_info = self.protocol.load(self.f)
            print_debug("received response", res_info)
        except (EOFError, ConnectionResetError) as e:
            print('remote end disconnected.')
            return self.handle_receive_exception(e)
        except BaseException as e:
            print('malformed result? Got exception:')
            traceback.print_exc()
            return self.handle_receive_exception(e)
        req_id = res_info[0]
        async_res = self.reqs[req_id]
        async_res.set(res_info[1:])
        del self.reqs[req_id]
        return True
    def loop(self):
        while self.receive():
            pass
