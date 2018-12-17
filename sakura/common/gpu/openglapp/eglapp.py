import io
from gevent.queue import Queue, Empty
from sakura.common.gpu import libegl
from sakura.common.gpu.openglapp.base import OpenglAppBase
from sakura.common.gpu.tools import write_jpg

MIN_RATE =  0.5      # frames per second (if no change)

class EGLApp(OpenglAppBase):

    def __init__ (self, handler):
        OpenglAppBase.__init__ (self, handler)
        self.change_queue   = Queue()
        self.ctx = libegl.EGLContext()

    def notify_change(self):
        self.change_queue.put(1)

    def window_resize(self, w, h):
        self.ctx.resize(w, h)

    def prepare_display(self):
        self.ctx.make_current()

    def release_display(self):
        pass

    def init(self, w=None, h=None):
        if w:   self.width = w
        if h:   self.height = h

        self.ctx.initialize(self.width, self.height)
        self.ctx.make_current()

        self.handler.init()

    def stream_jpeg_frames(self):
        f = io.BytesIO()
        while True:
            try:
                self.change_queue.get(timeout=1/MIN_RATE)
            except Empty:
                pass
            # if there were more change notifications queued,
            # ignore them (we are late)
            while not self.change_queue.empty():
                self.change_queue.get()     # pop
            self.ctx.make_current()
            self.display()
            write_jpg(f, self.width, self.height)
            yield f.getvalue()
            f.seek(0)
            f.truncate()

