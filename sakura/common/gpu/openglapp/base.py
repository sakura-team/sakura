import io, gevent, weakref
from sakura.common.events import EventSourceMixin
from sakura.common.gpu.tools import write_rgb_frame
from sakura.common.gpu.openglapp import MouseMoveReporting
from sakura.common.gpu.openglapp.streamer import Streamer

class OpenglAppBase(EventSourceMixin):
    def __init__ (self, handler):
        self.handler = handler
        self.handler.app = self
        self.width   = 0
        self.height  = 0
        self.label   = getattr(handler, "label", 'Unnamed 3D App')
        self.mouse_move_reporting = \
                       getattr(handler, "mouse_move_reporting",
                       MouseMoveReporting.LEFT_CLICKED)
        self.url_pattern = None
        self.active_streamers = []
        self.greenlets = []

    def cleanup_streamers(self):
        self.active_streamers = [ ref for ref in self.active_streamers \
                                    if ref() is not None ]

    @property
    def active_streamer(self):
        self.cleanup_streamers()
        if len(self.active_streamers) == 0:
            return None
        return self.active_streamers[-1]()  # top of the stack

    def is_streamer_active(self, streamer):
        return streamer is self.active_streamer

    def set_streamer_active(self, streamer):
        self.active_streamers.append(weakref.ref(streamer))

    @property
    def currently_streamed(self):
        return self.active_streamer is not None

    @property
    def streaming_is_busy(self):
        if self.active_streamer is None:
            return False
        if self.active_streamer.change_queue.empty():
            return False
        return True

    def plan_periodic_task(self, callback, period):
        def task_loop():
            while True:
                gevent.sleep(period)
                if not self.streaming_is_busy:
                    self.make_current()
                    callback()
                    self.notify_change()
        g_task = gevent.Greenlet.spawn(task_loop)
        self.greenlets.append(g_task)

    def pack(self):
        return { "video_url_pattern": self.url_pattern,
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

    def on_wheel(self, delta):
        self.make_current()
        self.handler.on_wheel(delta)
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
        if self.active_streamer is not None and not self.streaming_is_busy:
            self.active_streamer.change_queue.put(1)

    def get_streamer(self, width, height):
        return Streamer(app=self, width=width, height=height)

    def get_frame(self, unchanged):
        self.make_current()
        if not unchanged:
            self.display()  # really draw a new frame
        f = io.BytesIO()
        write_rgb_frame(f, self.width, self.height)
        return f.getvalue()

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
