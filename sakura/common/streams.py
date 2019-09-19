import sys, gevent, socket
from contextlib import contextmanager
from gevent.socket import wait_read
from gevent.event import AsyncResult

class StdinWrapper:
    def local_wait_read(self):
        wait_read(sys.__stdin__.fileno())
    def read(self, n = None):
        self.local_wait_read()
        return sys.__stdin__.read(n)
    def readline(self):
        self.local_wait_read()
        return sys.__stdin__.readline()
    def __getattr__(self, attr):
        return getattr(sys.__stdin__, attr)

class LocalStreams:
    def __init__(self):
        self.stdin = StdinWrapper()
        self.stdout = sys.__stdout__
        self.stderr = sys.__stderr__

# this allows to re-evaluate the value of property 'redirector.streams'
# each time a standard stream is used (i.e. one of its attributes is accessed)
class StreamProxy:
    def __init__(self, redirector, stream_name):
        self.redirector = redirector
        self.stream_name = stream_name
    def __getattr__(self, attr):
        return getattr(getattr(self.redirector.streams, self.stream_name), attr)

class Redirector:
    def __init__(self):
        self.local_streams = LocalStreams()
    @property
    def streams(self):
        curr_greenlet = gevent.getcurrent()
        return getattr(curr_greenlet, '__streams__', self.local_streams)
    @property
    def stdin(self):
        return StreamProxy(self, 'stdin')
    @property
    def stdout(self):
        return StreamProxy(self, 'stdout')
    @property
    def stderr(self):
        return StreamProxy(self, 'stderr')
    @classmethod
    def set_streams(cls, streams):
        curr_greenlet = gevent.getcurrent()
        curr_greenlet.__streams__ = streams
    @classmethod
    def unset_streams(cls):
        curr_greenlet = gevent.getcurrent()
        delattr(curr_greenlet, '__streams__')

def enable_standard_streams_redirection():
    redirector = Redirector()
    sys.stdin = redirector.stdin
    sys.stdout = redirector.stdout
    sys.stderr = redirector.stderr

@contextmanager
def get_stream_redirector(streams):
    Redirector.set_streams(streams)
    try:
        yield None
    finally:
        Redirector.unset_streams()

class StreamRedirectorProxy:
    def __init__(self, obj, streams):
        self.obj = obj
        self.get_stream_redirector = lambda: get_stream_redirector(streams)
    def __getattr__(self, attr):
        with self.get_stream_redirector():
            return getattr(self.obj, attr)

