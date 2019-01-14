import io
from gevent.queue import Queue, Empty
from sakura.common.gpu import libegl
from sakura.common.gpu.openglapp.base import OpenglAppBase
from sakura.common.gpu.tools import write_jpg

# parameters of jpeg streams
# * we compute images as soon as possible, with default jpeg quality (low quality)
# * if we are idle during MAX_LOW_QUALITY_DELAY seconds, we compute and deliver a
#   high quality image
# * if we are still idle after MAX_HIGH_QUALITY_DELAY, we deliver the same high
#   quality image again (in order to avoid timeouts on the browser)
MAX_LOW_QUALITY_DELAY =  0.1
MAX_HIGH_QUALITY_DELAY = 2.0

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
        high_quality = False
        while True:
            timed_out = False
            if high_quality:
                timeout = MAX_HIGH_QUALITY_DELAY
            else:
                timeout = MAX_LOW_QUALITY_DELAY
            try:
                self.change_queue.get(timeout=timeout)
                # if there were more change notifications queued,
                # ignore them (we are late)
                while not self.change_queue.empty():
                    self.change_queue.get()     # pop
            except Empty:
                timed_out = True
            high_quality = timed_out
            self.ctx.make_current()
            if not timed_out:   # otherwise display did not change
                self.display()
            quality = 95 if high_quality else 75
            write_jpg(f, self.width, self.height, quality = quality)
            yield f.getvalue()
            f.seek(0)
            f.truncate()

