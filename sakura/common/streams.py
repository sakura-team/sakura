import sys, gevent, socket, os.path
from contextlib import contextmanager
from gevent.socket import wait_read
from gevent.event import AsyncResult

def get_local_desc():
    short_args = [ os.path.basename(sys.argv[0]) ] + sys.argv[1:]
    return ' '.join(short_args) + " (on host '" + socket.gethostname() + "')"

LOCAL_DESC = get_local_desc()

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
    def describe(self):
        return LOCAL_DESC

LOCAL_STREAMS = LocalStreams()

CB_END_OF_REDIRECTION = None

def on_end_of_redirection(cb):
    global CB_END_OF_REDIRECTION
    CB_END_OF_REDIRECTION = cb

# In order to associate standard streams redirection
# to a given source file, the import system defines
# a module attribute called "__streams__".
# This function looks for this optional attribute
# in the frames of the stack, starting from the most
# in-depth frame.
last_streams = None
def get_streams_def(f):
    global last_streams
    while f:
        streams = f.f_globals.get('__streams__')
        if streams is not None:
            if last_streams is not streams:
                sys.__stdout__.write('Temporary std streams redirection to: ' + streams.describe() + '\n')
                last_streams = streams
            return streams
        f = f.f_back
    # if not found, select local streams
    if last_streams is not None:
        last_streams = None
        sys.__stdout__.write('End of redirection.\n')
        if CB_END_OF_REDIRECTION is not None:
            CB_END_OF_REDIRECTION()
    return LOCAL_STREAMS

class FailsafeMethod:
    def __init__(self, method, fallback_method):
        self.method, self.fallback_method = method, fallback_method
    def __call__(self, *args, **kwargs):
        try:
            return self.method(*args, **kwargs)
        except:
            return self.fallback_method(*args, **kwargs)

# this allows to re-evaluate the value of property 'redirector.streams'
# each time a standard stream is used (i.e. one of its attributes is accessed)
class StreamProxy:
    def __init__(self, redirector, stream_name):
        self.redirector = redirector
        self.stream_name = stream_name
    def __getattr__(self, method_name):
        streams = self.redirector.streams
        stream = getattr(streams, self.stream_name)
        method = getattr(stream, method_name)
        if streams is LOCAL_STREAMS:
            return method
        else:
            fallback_stream = getattr(LOCAL_STREAMS, self.stream_name)
            fallback_method = getattr(fallback_stream, method_name)
            return FailsafeMethod(method, fallback_method)

class Redirector:
    @property
    def streams(self):
        frame = sys._getframe().f_back
        return get_streams_def(frame)
    @property
    def stdin(self):
        return StreamProxy(self, 'stdin')
    @property
    def stdout(self):
        return StreamProxy(self, 'stdout')
    @property
    def stderr(self):
        return StreamProxy(self, 'stderr')

def enable_standard_streams_redirection():
    redirector = Redirector()
    sys.stdin = redirector.stdin
    sys.stdout = redirector.stdout
    sys.stderr = redirector.stderr
