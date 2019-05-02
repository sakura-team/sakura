import io, gevent
from gevent.queue import Queue, Empty
from sakura.common.events import EventSourceMixin
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

class Streamer:
    def __init__(self, app, width, height):
        self.change_queue = Queue()
        self.app = app
        self.width = width
        self.height = height

    @property
    def active(self):
        return self.app.is_streamer_active(self)

    def __del__(self):
        self.app.drop_streamer(self)

    def stream_jpeg_frames(self):
        high_quality = False
        i = 0
        self.app.on_resize(self.width, self.height)
        while True:
            timed_out = False
            if i == 0:
                timeout = None  # wait long enough for 1st frame
            elif high_quality:
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
            if not self.active:
                break
            high_quality = timed_out
            quality = 95 if high_quality else 75
            #print(i, timed_out)
            frame = self.app.get_frame(unchanged = timed_out)
            #with open('frames/%dx%d-%02d.jpg' % (self.app.width, self.app.height, i), 'wb') as g:
            #    g.write(frame)
            yield frame
            i += 1

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
        if SAKURA_DISPLAY_STREAMING:
            self.streamed = True
            self.streamers = []
        else:
            self.streamed = False
        self.greenlets = []

    @property
    def active_streamer(self):
        if not self.streamed:
            return None
        if len(self.streamers) == 0:
            return None
        return self.streamers[-1]  # top of the stack

    def is_streamer_active(self, streamer):
        return streamer is self.active_streamer

    def drop_streamer(self, streamer):
        self.streamers.remove(streamer)

    @property
    def currently_streamed(self):
        return self.streamed and len(self.streamers) > 0

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
        return { "mjpeg_url_pattern": self.url_pattern,
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

    def stream_jpeg_frames(self, width, height):
        streamer = Streamer(app=self, width=width, height=height)
        self.streamers.append(streamer)
        yield from streamer.stream_jpeg_frames()

    def get_frame(self, unchanged):
        quality = 95 if unchanged else 75
        self.make_current()
        if not unchanged:
            self.display()  # really draw a new frame
        f = io.BytesIO()
        write_jpg(f, self.width, self.height, quality = quality)
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
