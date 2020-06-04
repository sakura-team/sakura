import collections, itertools, io, sys, traceback, builtins, random
import gevent.pool
from os import getpid
from gevent.queue import Queue
from gevent.event import AsyncResult
from sakura.common.tools import monitored, ObservableEvent
from sakura.common.errors import APIReturningError, APIRemoteError, \
                                 IOHoldException, APIInvalidRequest, \
                                 IOReadException, IOWriteException
from sakura.common import errors
from sakura.common.io.debug import print_debug
from sakura.common.io.held import HeldObjectsStore
from sakura.common.io.tools import void_context_manager, traverse
from sakura.common.io.const import IO_REQ_FUNC_CALL, IO_REQ_ATTR, \
        IO_RESP_TRANSFERED, IO_RESP_HELD, IO_RESP_REQUEST_ERROR, IO_RESP_STOP_ITERATION, \
        IO_ARG_HELD, IO_ARG_TRANSFERED, IO_TRANSFERABLES
from sakura.common.io.proxy import Proxy

class APIEndpoint:
    def __init__(self, f, protocol, local_api,
                 session_wrapper = void_context_manager,
                 silent_disconnect = False):
        self.f = f
        self.protocol = protocol
        self.local_api = local_api
        self.session_wrapper = session_wrapper
        self.pool = gevent.pool.Group()
        self.held_objects = HeldObjectsStore.get()
        self.proxy = Proxy(self, ('local_api',))
        self.reqs = {}
        self.req_ids = itertools.count()
        self.on_remote_exception = ObservableEvent()
        self.remote_deleted_ids = []
        # redirect exceptions of all sub-greenlets to the same queue
        self.do_loop = monitored(self.do_loop)
        self.handle_message = monitored(
                self.handle_message, self.do_loop.out_queue)
        self.silent_disconnect = silent_disconnect
        if hasattr(self.protocol, 'is_transferable'):
            self.is_transferable = self.protocol.is_transferable
        else:
            self.is_transferable = lambda obj: isinstance(obj, IO_TRANSFERABLES)
        self.debug_prefix = ''.join(random.choice('/*-+') for i in range(4)) + ' '
    def print_debug(self, s, *args):
        print_debug(self.debug_prefix + s, *args)
    def loop(self):
        try:
            # start
            self.pool.spawn(self.do_loop)
            # wait for an exception
            self.do_loop.catch_issues()
        except EOFError:
            return  # leave the loop
    def do_loop(self):
        while True:
            if not self.handle_next_message():
                break
        raise EOFError
    def handle_next_message(self):
        try:
            msg = self.protocol.load(self.f)
        except BaseException as e:
            if isinstance(e, (EOFError, ConnectionResetError, IOReadException)):
                if self.silent_disconnect is False:
                    print('remote end disconnected!')
            elif isinstance(e, APIInvalidRequest):
                print('invalid request.')
            else:
                print('malformed request? Got exception:')
                traceback.print_exc()
            if self.silent_disconnect is False:
                self.handle_receive_exception(e)
                print('closing this api channel.')
            if not self.f.closed:
                self.f.close()
            return False  # we should stop
        self.pool.spawn(self.handle_message, *msg)
        return True
    def handle_message(self, req_id, msg_type, *msg_args):
        msg = (req_id, msg_type) + tuple(msg_args)
        if msg_type in (IO_REQ_FUNC_CALL, IO_REQ_ATTR):
            self.print_debug('received request', msg)
            self.debug_prefix += '  '
            self.handle_request(req_id, msg_type, *msg_args)
        else:
            self.debug_prefix = self.debug_prefix[:-2]
            self.print_debug('received response', msg)
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
                print_debug(traceback.format_exc())
                data = getattr(e, 'data', {})
                out = (IO_RESP_REQUEST_ERROR, e.__class__.__name__, str(e), data)
            # send response
            self.debug_prefix = self.debug_prefix[:-2]
            try:
                self.protocol.dump((req_id,) + out, self.f)
                self.f.flush()
                self.print_debug("sent response", (req_id,) + out)
            except BaseException as e:
                print('could not send response:', e)
            self.held_objects.flush()
            self.flush_remote_deleted_ids()
    def handle_response(self, req_id, *resp_info):
        async_res = self.reqs[req_id]
        async_res.set(resp_info)
        del self.reqs[req_id]
    def possibly_hold(self, res):
        if not self.is_transferable(res):
            # res should not be serialized,
            # hold it locally.
            held_info = self.hold(res)
            # notify remote end
            return (IO_RESP_HELD,) + held_info
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
                protected_args, protected_kwargs = more
                args, kwargs = self.parse_protected_args(protected_args, protected_kwargs)
                return obj(*args, **kwargs)
        except AttributeError as e:
            raise APIInvalidRequest(str(e))
    def delete_held(self, *held_ids):
        for held_id in held_ids:
            del self.held_objects[held_id]
    def delete_remotely_held(self, remote_held_id):
        self.remote_deleted_ids.append(remote_held_id)
    def flush_remote_deleted_ids(self):
        remote_deleted_ids = self.remote_deleted_ids
        if len(remote_deleted_ids) == 0:
            return
        self.remote_deleted_ids = []
        # if remote end is down, there is no remote object to delete...
        if not self.f.closed:
            self.remote_call_raw(IO_REQ_FUNC_CALL, ('delete_held',), tuple(remote_deleted_ids), {})
    def func_call(self, path, args=(), kwargs={}):
        return self.remote_call(IO_REQ_FUNC_CALL, path, args, kwargs)
    def attr_call(self, path):
        return self.remote_call(IO_REQ_ATTR, path)
    def protect_args(self, args, kwargs):
        protected_args = ()
        for arg in args:
            if self.is_transferable(arg):
                protected_args += ((IO_ARG_TRANSFERED, arg),)
            else:
                held_info = self.hold(arg)
                protected_args += ((IO_ARG_HELD, held_info),)
        protected_kwargs = {}
        for k, v in kwargs.items():
            if self.is_transferable(v):
                protected_kwargs[k] = (IO_ARG_TRANSFERED, v)
            else:
                held_info = self.hold(v)
                protected_kwargs[k] = (IO_ARG_HELD, held_info)
        return protected_args, protected_kwargs
    def parse_protected_args(self, protected_args, protected_kwargs):
        args = ()
        for v1, v2 in protected_args:
            if v1 == IO_ARG_TRANSFERED:
                args += (v2,)
            else:
                held_info = v2
                args += (HeldObjectsStore.get_proxy(self, held_info),)
        kwargs = {}
        for k, v in protected_kwargs.items():
            if v[0] == IO_ARG_TRANSFERED:
                kwargs[k] = v[1]
            else:
                held_info = v[1]
                kwargs[k] = HeldObjectsStore.get_proxy(self, held_info)
        return args, kwargs
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
            held_info = res[1:]
            return HeldObjectsStore.get_proxy(self, held_info)
    def remote_call_raw(self, *req):
        if req[0] == IO_REQ_FUNC_CALL:
            args, kwargs = req[2], req[3]
            req = req[0:2] + self.protect_args(args, kwargs)
        req_id = self.req_ids.__next__()
        async_res = AsyncResult()
        self.reqs[req_id] = async_res
        self.print_debug("sent request", (req_id,) + req)
        self.protocol.dump((req_id,) + req, self.f)
        self.f.flush()
        self.debug_prefix += '  '
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
