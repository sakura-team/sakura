import sys
from contextlib import contextmanager

@contextmanager
def get_stream_redirector(streams):
    sys.stdin = streams.stdin
    sys.stdout = streams.stdout
    sys.stderr = streams.stderr
    try:
        yield None
    finally:
        sys.stdin = sys.__stdin__
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

class StreamRedirectorProxy:
    def __init__(self, obj, streams):
        self.obj = obj
        self.get_stream_redirector = lambda: get_stream_redirector(streams)
    def __getattr__(self, attr):
        with self.get_stream_redirector():
            return getattr(self.obj, attr)

