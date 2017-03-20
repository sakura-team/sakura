import sys, gevent

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
            setattr(self, k, v)
    def _asdict(self):
        return self.__dict__.copy()
