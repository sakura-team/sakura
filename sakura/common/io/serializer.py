from gevent.lock import BoundedSemaphore

class Serializer(object):
    """Serialize read and write operations on a given file or socket object"""
    def __init__(self, f):
        self.f = f
        self.write_semaphore = BoundedSemaphore()
        self.read_semaphore = BoundedSemaphore()
    def do_op(self, lock, op, args):
        with lock:
            m = getattr(self.f, op)
            return m(*args)
    def do_op_w(self, op, *args):
        return self.do_op(self.write_semaphore, op, args)
    def do_op_r(self, op, *args):
        return self.do_op(self.read_semaphore, op, args)
    def write(self, *args):
        return self.do_op_w('write', *args)
    def read(self, *args):
        return self.do_op_r('read', *args)
    def readline(self):
        return self.do_op_r('readline')
    def close(self):
        return self.do_op_w('close')
    def flush(self):
        return self.do_op_w('flush')
    def recv(self, *args):
        return self.do_op_r('recv', *args)
    def receive(self, *args):
        return self.do_op_r('receive', *args)
    def send(self, *args):
        return self.do_op_w('send', *args)
    def fileno(self):
        return self.do_op_w('fileno')
    def __getattr__(self, attr):
        return getattr(self.f, attr)
