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

def SimpleAttrContainer(*attrs):
    class Cls:
        __slots__ = attrs
        def __init__(self, *args):
            for attr, v in zip(attrs, args):
                setattr(self, attr, v)
    return Cls
