import io, gevent
from gevent.queue import Queue, Empty
from sakura.common.gpu.tools import write_jpg
from sakura.common.gpu.openglapp import \
                MouseMoveReporting, SAKURA_DISPLAY_STREAMING

# parameters of jpeg streams
# * we compute images as soon as possible, with default jpeg quality (low quality)
# * if we are idle during MAX_LOW_QUALITY_DELAY seconds, we compute and deliver a
#   high quality image
# * if we are still idle after MAX_HIGH_QUALITY_DELAY, we deliver the same high
#   quality image again (in order to avoid timeouts on the browser)
MAX_LOW_QUALITY_DELAY =  0.1
MAX_HIGH_QUALITY_DELAY = 2.0

class OpenglAppBase:
    def __init__ (self, handler):
        self.handler = handler
        self.width   = 0
        self.height  = 0
        self.label   = getattr(handler, "label", 'Unnamed 3D App')
        self.mouse_move_reporting = \
                       getattr(handler, "mouse_move_reporting",
                       MouseMoveReporting.LEFT_CLICKED)
        self.url     = None
        if SAKURA_DISPLAY_STREAMING:
            self.streamed = True
            self.change_queue   = Queue()
        else:
            self.streamed = False
        self.greenlets = []

    def plan_periodic_task(self, callback, period):
        def task_loop():
            while True:
                gevent.sleep(period)
                self.make_current()
                callback()
                self.notify_change()
        g_task = gevent.Greenlet.spawn(task_loop)
        self.greenlets.append(g_task)

    def pack(self):
        return { "mjpeg_url": self.url,
                 "mouse_move_reporting": self.mouse_move_reporting.name }

    def on_resize(self, w, h):
        w, h = int(w), int(h)
        self.make_current()
        if (self.width, self.height) != (w, h):
            self.width, self.height = w, h
            self.window_resize(w, h)
        self.handler.on_resize(w, h)
        self.notify_change()

    def on_key_press(self, key, x, y):
        self.make_current()
        self.handler.on_key_press(key, x, y)
        self.notify_change()

    def on_mouse_motion(self, x, y):
        self.make_current()
        self.handler.on_mouse_motion(x, y)
        self.notify_change()

    def on_mouse_click(self, button, state, x, y):
        self.make_current()
        self.handler.on_mouse_click(button, state, x, y)
        self.notify_change()

    def display(self):
        self.make_current()
        self.prepare_display()
        self.handler.display()
        self.release_display()

    def fire_event(self, event_type, *args, **kwargs):
        return getattr(self, event_type)(*args, **kwargs)

    def notify_change(self):
        # local display
        self.trigger_local_display()
        # remote display
        if self.streamed:
            self.change_queue.put(1)

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
            self.make_current()
            if not timed_out:   # otherwise display did not change
                self.display()
            quality = 95 if high_quality else 75
            write_jpg(f, self.width, self.height, quality = quality)
            yield f.getvalue()
            f.seek(0)
            f.truncate()

    def trigger_local_display(self):
        raise NotImplementedError   # should be implemented in subclass

    def window_resize(self, w, h):
        raise NotImplementedError   # should be implemented in subclass

    def make_current(self):
        raise NotImplementedError   # should be implemented in subclass

    def prepare_display(self):
        raise NotImplementedError   # should be implemented in subclass

    def release_display(self):
        raise NotImplementedError   # should be implemented in subclass

    def init(self, w=None, h=None):
        raise NotImplementedError   # should be implemented in subclass

    def __del__(self):
        for g_task in self.greenlets:
            g_task.kill()

