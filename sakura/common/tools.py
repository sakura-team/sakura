import os, sys, gevent, json, pickle
from pathlib import Path
from gevent.queue import Queue
import ctypes
from gevent.subprocess import run, PIPE, STDOUT
import numpy as np

class StdoutProxy(object):
    def __init__(self, stdout):
        self.stdout = stdout
    def write(self, s):
        self.stdout.write(s)
        self.stdout.flush()
    def __getattr__(self, attr):
        return getattr(self.stdout, attr)

def set_unbuffered_stdout():
    sys.stdout = StdoutProxy(sys.stdout)

def wait_greenlets(*greenlets):
    gevent.joinall(greenlets, count=1)

class SimpleAttrContainer:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            v = self.load_val(v)
            setattr(self, k, v)
    def load_val(self, v):
        if isinstance(v, dict):
            v = SimpleAttrContainer(**v)
        elif isinstance(v, tuple):
            v = tuple(self.load_val(v2) for v2 in v)
        elif isinstance(v, list):
            v = list(self.load_val(v2) for v2 in v)
        return v
    def _asdict(self):
        return self.__dict__.copy()

class MonitoredFunc(object):
    def __init__(self, func, out_queue):
        self.func = func
        if out_queue is None:
            self.out_queue = Queue()
        else:
            self.out_queue = out_queue
    def __call__(self, *args, **kwargs):
        try:
            res = self.func(*args, **kwargs)
        except BaseException as e:
            # propagate exception to monitoring greenlet
            self.out_queue.put(e)
        self.out_queue.put(None)
    def catch_issues(self):
        # wait for end or exception
        while True:
            out = self.out_queue.get()
            if isinstance(out, KeyboardInterrupt):
                break
            elif isinstance(out, BaseException):
                raise out

# decorator allowing to catch exceptions in children greenlets
def monitored(func, out_queue = None):
    return MonitoredFunc(func, out_queue)

OverriddenObjectClasses = {}

def override_object(obj, override):
    bases = override.__class__, obj.__class__
    if bases not in OverriddenObjectClasses:
        # Favour methods of override over original object
        # (thus the subclassing)
        # Favour attributes of override over original object
        # (thus the __getattr__ method)
        class OverriddenObject(override.__class__, obj.__class__):
            def __init__(self, obj, override):
                self.override = override
                self.obj = obj
            def __getattr__(self, attr):
                if hasattr(self.override, attr):
                    return getattr(self.override, attr)
                else:
                    return getattr(self.obj, attr)
        OverriddenObjectClasses[bases] = OverriddenObject
    cls = OverriddenObjectClasses[bases]
    return cls(obj, override)

class Enum:
    def __init__(self, words):
        self._words = words
        for val, word in enumerate(words):
            setattr(self, word, val)
    def name(self, val):
        return self._words[val]
    def value(self, word):
        return getattr(self, word)
    def __len__(self):
        return len(self._words)

def make_enum(*words):
    return Enum(words)

# only load libraries if they are needed
class LazyFuncCaller:
    libs = {}
    def __init__(self, lib_name, func_name):
        self.lib_name = lib_name
        self.func_name = func_name
    def __call__(self, *args, **kwargs):
        if self.lib_name not in LazyFuncCaller.libs:
            LazyFuncCaller.libs[self.lib_name] = ctypes.CDLL(self.lib_name)
        func = getattr(LazyFuncCaller.libs[self.lib_name], self.func_name)
        return func(*args, **kwargs)

# provide rollback capability to classes
class TransactionMixin:
    def __init__(self):
        self.rollback_cbs = []
    def rollback(self):
        for cb in reversed(self.rollback_cbs):
            cb()
        self.rollback_cbs = []
    def add_rollback_cb(self, cb):
        self.rollback_cbs += [ cb ]
    def __enter__(self):
        return self
    def __exit__(self, type, value, traceback):
        self.rollback()

class ObservableEvent:
    def __init__(self):
        self.observer_callbacks = []
    def subscribe(self, cb):
        self.observer_callbacks.append(cb)
    def unsubscribe(self, cb):
        if cb in self.observer_callbacks:
            self.observer_callbacks.remove(cb)
    def notify(self, *args, **kwargs):
        # we work on a copy because running a callback
        # might actually recursively call this method...
        callbacks = set(self.observer_callbacks)
        obsoletes = set()
        for cb in callbacks:
            try:
                cb(*args, **kwargs)
            except:
                # obsolete callback
                obsoletes.add(cb)
        for cb in obsoletes:
            self.unsubscribe(cb)

def debug_ending_greenlets():
    import gc, traceback, greenlet
    for ob in gc.get_objects():
        if not isinstance(ob, greenlet.greenlet):
            continue
        if not ob:
            continue
        print()
        print('GREENLET:')
        print(ob)
        print(''.join(traceback.format_stack(ob.gr_frame)))

class StatusMixin:
    def pack_status_info(self):
        res = {}
        if hasattr(self, 'enabled'):
            res.update(enabled = self.enabled)
            if not self.enabled:
                res.update(disabled_message = self.disabled_message)
        if getattr(self, 'enabled', True) and hasattr(self, 'warning_message'):
            res.update(warning_message = self.warning_message)
        return res

def run_cmd(cmd, cwd=None, **options):
    if cwd is not None:
        saved_cwd = Path.cwd()
        os.chdir(str(cwd))
    print(str(Path.cwd()) + ': ' + cmd)
    status = run(cmd, shell=True, stdout=PIPE, stderr=STDOUT, **options)
    if status.returncode != 0:
        print(status.stdout)
        raise Exception(cmd + ' failed!')
    if cwd is not None:
        os.chdir(str(saved_cwd))
    return status.stdout.decode(sys.stdout.encoding)

def yield_operator_subdirs(repo_dir):
    # find all operator.py file
    for op_py_file in repo_dir.glob('**/operator.py'):
        op_dir = op_py_file.parent
        # verify we also have the icon file
        if not (op_dir / 'icon.svg').exists():
            continue
        # discard probably unwanted ones (virtual env, hidden files)
        op_subpath = str(op_dir.relative_to(repo_dir))
        if '/venv' in op_subpath or '/.' in op_subpath:
            continue
        # ok for this one
        yield op_dir

class JsonProtocol:
    def adapt(self, obj):
        if isinstance(obj, str) and obj.startswith('__bytes_'):
            return bytes.fromhex(obj[8:])
        if isinstance(obj, (tuple, list)):
            return tuple(self.adapt(item) for item in obj)
        elif isinstance(obj, dict):
            return { self.adapt(k): self.adapt(v) for k, v in obj.items() }
        else:
            return obj
    def load(self, f):
        return self.adapt(json.load(f))
    def fallback_handler(self, obj):
        if isinstance(obj, bytes):
            return '__bytes_' + obj.hex()
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        else:
            import traceback; traceback.print_stack()
            raise TypeError(
                "Unserializable object {} of type {}".format(obj, type(obj))
            )
    def dump(self, obj, f):
        try:
            # json.dump() function causes performance issues
            # because it performs many small writes on f.
            # So we json-encode in a string (json.dumps)
            # and then write this whole string at once.
            res_json = json.dumps(obj,
                separators=(',', ':'),
                default=self.fallback_handler)
            f.write(res_json)
        except BaseException as e:
            print('FAILED to serialize an object, re-raise exception.')
            print('object is', obj)
            raise

class ChunkedIO:
    CHUNK_SIZE = 4096
    def __init__(self, f):
        self.f = f
    def write(self, data):
        while len(data) > 0:
            self.f.write(data[:self.CHUNK_SIZE])
            data = data[self.CHUNK_SIZE:]
    def flush(self):
        self.f.flush()
    def read(self, n = None):
        if n is None:
            return self.f.read()
        chunks = []
        while n > 0:
            chunk_len = min(n, self.CHUNK_SIZE)
            chunk = self.f.read(chunk_len)
            if len(chunk) == 0:
                break
            n -= len(chunk)
            chunks.append(chunk)
        return b''.join(chunks)
    def readline(self):
        return self.f.readline()

JSON_PROTOCOL = JsonProtocol()

class FastChunkedPickle:
    def _get_chunked_io(self, f):
        chunked_io = getattr(f, '_chunked_io', None)
        if chunked_io is None:
            chunked_io = ChunkedIO(f)
            setattr(f, '_chunked_io', chunked_io)
        return chunked_io
    def load(self, f):
        return pickle.load(self._get_chunked_io(f))
    def dump(self, obj, f):
        # Default pickle protocol is version 3 (since python 3).
        # Protocol version 4 mainly brings framing, which obviously improves performance
        # when reading a stream. It is available since python 3.4.
        return pickle.dump(obj, self._get_chunked_io(f), protocol = 4)

FAST_PICKLE = FastChunkedPickle()

class MonitoredList:
    """Wrapper around the 'list' class that can notify about changes."""
    def __init__(self, *args):
        MonitoredList._class_init()
        self.backend = list(*args)
        self.on_change = ObservableEvent()
    @classmethod
    def _class_init(cls):
        if not hasattr(cls, 'append'):  # if not done yet
            for method_name in ('append clear extend insert pop remove reverse sort ' +
                                '__setitem__ __delitem__').split():
                cls._attach_method(method_name, True)
            for method_name in ('index ' +
                                '__contains__ __getitem__ __iter__ __len__ __repr__ __reversed__').split():
                cls._attach_method(method_name, False)
    @classmethod
    def _attach_method(cls, method_name, alter):
        def mlist_method(self, *args, **kwargs):
            backend_method = getattr(self.backend, method_name)
            res = backend_method(*args, **kwargs)
            if alter:
                self.on_change.notify()
            return res
        setattr(cls, method_name, mlist_method)
