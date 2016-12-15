from gevent.queue import Queue

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
            if isinstance(out, BaseException):
                raise out

# decorator allowing to catch exceptions in children greenlets
def monitored(func):
    return MonitoredFunc(func)

