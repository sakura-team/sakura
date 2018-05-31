import sys, gevent
from gevent.queue import Queue

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
    def __init__(self, func):
        self.func = func
        self.out_queue = Queue()
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
def monitored(func):
    return MonitoredFunc(func)

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
