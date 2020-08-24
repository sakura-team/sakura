import gevent
from gevent.queue import Queue

class StreamBgThread:
    def __init__(self, it, out_queue):
        self.out_queue = out_queue
        self.in_queue = Queue()
        self._iterator = it
        self.state = 'INIT'
    def spawn(self):
        self.greenlet = gevent.spawn(self._run)
        self.step()
    def _run(self):
        while True:
            if self.in_queue.qsize() > 0 or self.state in ('PAUSED', 'INIT'):
                evt_args = self.in_queue.get()
                if evt_args[0] == 'START':
                    self.state = 'STARTED'
                elif evt_args[0] == 'STEP':
                    self.state = 'STEP'
                elif evt_args[0] == 'PAUSE':
                    self.state = 'PAUSED'
                elif evt_args[0] == 'QUIT':
                    break
                continue
            try:
                chunk = next(self._iterator)
            except StopIteration:
                self.out_queue.put(('STREAM_END',))
                self.state = 'END'
                break
            self.out_queue.put(('CHUNK', chunk))
            if self.state == 'STEP':
                self.state = 'PAUSED'
    def start(self):
        if self.state != 'END':
            self.in_queue.put(('START',))
    def pause(self):
        if self.state != 'END':
            self.in_queue.put(('PAUSE',))
    def step(self):
        if self.state != 'END':
            self.in_queue.put(('STEP',))
    def quit(self):
        if self.state != 'END':
            self.in_queue.put(('QUIT',))
        self.greenlet.join()
