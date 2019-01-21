import os, sys, gevent
from pathlib import Path
from gevent.queue import Queue
import ctypes
from gevent.subprocess import run, PIPE, STDOUT

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
    def notify(self, *args, **kwargs):
        for cb in self.observer_callbacks:
            cb(*args, **kwargs)

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
