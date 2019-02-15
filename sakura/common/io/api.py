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
from sakura.common.io.tools import void_context_manager, traverse
from sakura.common.io.const import IO_REQ_FUNC_CALL, IO_REQ_ATTR, \
        IO_RESP_TRANSFERED, IO_RESP_HELD, IO_RESP_REQUEST_ERROR, IO_RESP_STOP_ITERATION, \
        IO_TRANSFERABLES
from sakura.common.io.proxy import Proxy

class APIEndpoint:
    def __init__(self, f, protocol, local_api, sync=False,
                 session_wrapper = void_context_manager):
        self.f = f
        self.protocol = protocol
        self.local_api = local_api
        self.session_wrapper = session_wrapper
        self.pool = gevent.pool.Group()
        self.held_objects = HeldObjectsStore.get()
        self.proxy = Proxy(self, ('local_api',))
        self.reqs = {}
        self.req_ids = itertools.count()
        self.sync = sync
        self.on_remote_exception = ObservableEvent()
        # redirect exceptions of all sub-greenlets to the same queue
        self.do_loop = monitored(self.do_loop)
        self.handle_message = monitored(
                self.handle_message, self.do_loop.out_queue)
        if hasattr(self.protocol, 'is_transferable'):
            self.is_transferable = self.protocol.is_transferable
        else:
            self.is_transferable = lambda obj: isinstance(obj, IO_TRANSFERABLES)
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
            self.handle_next_message()
    def handle_next_message(self):
        try:
            msg = self.protocol.load(self.f)
            print_debug('received message', str(msg))
        except BaseException as e:
            if isinstance(e, (EOFError, ConnectionResetError)):
                print('remote end disconnected!')
            elif isinstance(e, APIInvalidRequest):
                print('malformed request.')
            else:
                print('malformed request? Got exception:')
                traceback.print_exc()
            self.handle_receive_exception(e)
            raise   # we should stop
        self.pool.spawn(self.handle_message, *msg)
    def handle_message(self, req_id, msg_type, *msg_args):
        if msg_type in (IO_REQ_FUNC_CALL, IO_REQ_ATTR):
            self.handle_request(req_id, msg_type, *msg_args)
        else:
            self.handle_response(req_id, msg_type, *msg_args)
    def handle_request(self, req_id, req_type, *req_args):
        with self.session_wrapper():
            # run request
            try:
                res = self.do(req_type, *req_args)
                out = self.possibly_hold(res)
            except StopIteration:
                out = (IO_RESP_STOP_ITERATION,)
            except BaseException as e:
                data = getattr(e, 'data', {})
                out = (IO_RESP_REQUEST_ERROR, e.__class__.__name__, str(e), data)
            # send response
            try:
                self.protocol.dump((req_id,) + out, self.f)
                self.f.flush()
                print_debug("sent response", (req_id,) + out)
            except BaseException as e:
                print('could not send response:', e)
    def handle_response(self, req_id, *resp_info):
        async_res = self.reqs[req_id]
        async_res.set(resp_info)
        del self.reqs[req_id]
    def possibly_hold(self, res):
        if not self.is_transferable(res):
            # res should not be serialized,
            # hold it locally.
            held_id = self.hold(res)
            origin = getpid(), held_id
            if isinstance(res, Proxy):
                if res.__internals.get_origin() is not None:
                    origin = res.__internals.get_origin()
            # notify remote end
            return (IO_RESP_HELD, held_id) + origin
        # let result be transfered
        return (IO_RESP_TRANSFERED, res)
    def hold(self, obj):
        return self.held_objects.hold(obj)
    def do(self, req_type, path, *more):
        try:
            obj = traverse(self, path)
            if req_type == IO_REQ_ATTR:
                return obj
            elif req_type == IO_REQ_FUNC_CALL:
                args, kwargs = more
                return obj(*args, **kwargs)
        except AttributeError as e:
            raise APIInvalidRequest(str(e))
    def delete_held(self, held_id):
        del self.held_objects[held_id]
    def delete_remotely_held(self, remote_held_id):
        self.remote_call_raw(IO_REQ_FUNC_CALL, ('delete_held',), (remote_held_id,), {})
    def func_call(self, path, args=(), kwargs={}):
        return self.remote_call(IO_REQ_FUNC_CALL, path, args, kwargs)
    def attr_call(self, path):
        return self.remote_call(IO_REQ_ATTR, path)
    def remote_call(self, *req):
        res = self.remote_call_raw(*req)
        if res[0] == IO_RESP_TRANSFERED:
            # result was transfered, return it
            return res[1]
        if res[0] == IO_RESP_STOP_ITERATION:
            raise StopIteration
        if res[0] == IO_RESP_REQUEST_ERROR:
            cls_name, msg, data = res[1:]
            cls = getattr(errors, cls_name, None)
            if cls is None: cls = getattr(builtins, cls_name, None)
            if cls is None: cls = APIReturningError
            exc = cls(msg)
            exc.data = data
            self.on_remote_exception.notify(exc)
            raise exc
        if res[0] == IO_RESP_HELD:
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
                self.delete_remotely_held(remote_held_id)
                # return the object
                return obj
            remote_held_path = ('held_objects', (remote_held_id,))
            return Proxy(self, remote_held_path, origin,
                    delete_callback=lambda : self.delete_remotely_held(remote_held_id))
    def remote_call_raw(self, *req):
        req_id = self.req_ids.__next__()
        async_res = AsyncResult()
        self.reqs[req_id] = async_res
        print_debug("sent request", (req_id,) + req)
        self.protocol.dump((req_id,) + req, self.f)
        self.f.flush()
        # synchronous mode, for web api
        if self.sync:
            self.handle_next_message()
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
