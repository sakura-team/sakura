import os, sys, gevent, socket
from gevent.queue import Queue, Empty
from gevent.signal import signal, SIGINT
from gevent.socket import wait_read

def unbuffered(f, mode):
    # we need to duplicate the filedescriptor
    # in order to avoid the same filedescriptor
    # to be closed several times
    return os.fdopen(os.dup(f.fileno()), mode, 0)

# greenlet waiting on stdin and reporting input
# to out_queue.
class StdinMonitor:
    def __init__(self, out_queue):
        self.out_queue = out_queue
        self.in_queue = Queue()
        self.stdin = unbuffered(sys.stdin, 'rb')
    def spawn(self):
        self.greenlet = gevent.spawn(self._run)
    def _run(self):
        while self.in_queue.qsize() == 0:
            try:
                wait_read(self.stdin.fileno(), timeout=0.1)
            except socket.timeout:
                continue
            c = self.stdin.read(1)
            self.out_queue.put(('STDIN', c))
    def stop(self):
        self.in_queue.put(1)    # stop
        self.greenlet.join()

# If user types ctrl-C while we are waiting on a queue,
# another greenlet might be working and actually receive
# the KeyboardInterrupt exception. Using this procedure
# ensures that it will be the calling greenlet that will
# raise this exception.
def interruptible_queue_get(q, timeout=None):
    def handler():
        print('')   # print EOL
        q.put(KeyboardInterrupt)
    old_handler = signal(SIGINT, lambda *args: handler())
    while True:
        try:
            if timeout is None:
                res = q.get(timeout=0.2)
            else:
                res = q.get(timeout=timeout)
            break
        except Empty:
            if timeout is None:
                continue
            else:
                res = Empty
                break
    signal(SIGINT, old_handler)
    if res in (KeyboardInterrupt, Empty):
        raise res
    else:
        return res
