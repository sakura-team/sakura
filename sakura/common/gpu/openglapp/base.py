import io, gevent, shlex, fcntl, os, time, itertools, time
from subprocess import Popen, PIPE
from gevent.queue import Queue, Empty
from gevent.event import Event
from gevent.socket import wait_read, wait_write
from sakura.common.events import EventSourceMixin
from sakura.common.gpu.tools import write_bmp
from sakura.common.gpu.openglapp import \
                MouseMoveReporting, SAKURA_DISPLAY_STREAMING

# parameters of ffmpeg output video stream
# * FPS: frames per second
# * KEYFRAME_INTERVAL: caution not to increase this too much, because
#   it has an impact on the browser side (more data have to be buffered
#   in RAM)
FPS = 25
KEYFRAME_INTERVAL = 5
KEYFRAME_RATE = KEYFRAME_INTERVAL * FPS

# parameters of ffmpeg input frame stream
# * if there has been recent changes on the display, continue to input frames to ffmpeg
#   at FPS rate, for a small period of time (CHANGE_FLUSH_INTERVAL), to be sure those
#   changes are not buffered in ffmpeg output.
# * if we are idle for more time, lower down input frame rate according to MAX_INPUT_FRAME_INTERVAL.
CHANGE_FLUSH_INTERVAL = 0.5
MAX_INPUT_FRAME_INTERVAL = 2.0

FFMPEG_CMD_PATTERN = '''\
ffmpeg -y -f image2pipe -use_wallclock_as_timestamps 1 -probesize %(bmp_size)d -fflags nobuffer -max_delay 50000 -i - \
    -flush_packets 1 -tune zerolatency -vcodec libx264 -pix_fmt yuv420p -frag_duration 50000 -frag_size 1024 \
    -filter:v fps=fps=%(fps)d -g %(keyframe_rate)d -movflags +dash -max_delay 50000 -f mp4 - '''

mike_wait_time  = 0
mike_read_time  = 0
mike_back_time  = 0
mike_back_date  = time.time()
mike_nb_times   = 0

class Streamer:
    def __init__(self, app, width, height):
        self.change_queue = Queue()
        self.app = app
        self.width = width
        self.height = height
        self.ffmpeg = None

    @property
    def active(self):
        return self.app.is_streamer_active(self)

    def __del__(self):
        if self.ffmpeg is not None:
            self.ffmpeg.terminate()
        self.app.drop_streamer(self)

    def stream_bmp_frames(self):
        i = 0
        last = None
        last_update = None
        self.app.on_resize(self.width, self.height)
        while True:
            # in case we are both busy at inputting frames and at
            # reading ffmpeg output, favor the later
            gevent.idle()
            timed_out = False
            now = time.time()
            if last is not None:
                # if there has been a recent display update
                # continue input at FPS rate for a little period
                # to be sure ffmpeg output does not buffer those
                # updates too long.
                # otherwise (no change, same image), input frames
                # according to MAX_INPUT_FRAME_INTERVAL.
                if now - last_update < CHANGE_FLUSH_INTERVAL:
                    timeout = (last+ (1/FPS)) - now
                else:
                    timeout = (last + MAX_INPUT_FRAME_INTERVAL) - now
            else:
                timeout = 0
            #print(' -- timeout:', timeout)
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
            last = time.time()
            if last_update is None or not timed_out:
                last_update = last
            #print(' -- wait:', last-now)
            #print(i, timed_out)
            frame = self.app.get_frame(unchanged = timed_out)
            #with open('frames/%dx%d-%02d.bmp' % (self.app.width, self.app.height, i), 'wb') as g:
            #    g.write(frame)
            self.last_frame_input = time.time()
            #print(' -- get-frame:', self.last_frame_input-last)
            # next loop step will have to wait until at least one chunk is output from ffmpeg
            yield frame
            i += 1

    def feed_ffmpeg(self, it):
        for frame in it:
            wait_write(self.ffmpeg.stdin.fileno())
            self.ffmpeg.stdin.write(frame)
            self.ffmpeg.stdin.flush()

    def stream_video(self):
        # we peek the first frame, to get its size, and use it as a parameter to
        # ffmpeg option "-probesize"

        global mike_wait_time, mike_read_time
        global mike_back_time, mike_back_date, mike_nb_times

        it = self.stream_bmp_frames()
        first_frame = next(it)
        cmd = FFMPEG_CMD_PATTERN % dict(
                fps = FPS,
                keyframe_rate = KEYFRAME_RATE,
                bmp_size = len(first_frame)
        )
        self.ffmpeg = Popen(shlex.split(cmd), stdin=PIPE, stdout=PIPE, bufsize=0)
        rebuilt_it = itertools.chain([first_frame], it)

        gevent.Greenlet.spawn(self.feed_ffmpeg, rebuilt_it)
        #fcntl.fcntl(self.ffmpeg.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)
        while self.active:
            t = time.time()
            mike_back_time += t - mike_back_date

            wait_read(self.ffmpeg.stdout.fileno())
            mike_wait_time += time.time() - t

            t = time.time()
            out = self.ffmpeg.stdout.read(2048)
            if len(out) == 0:
                break
            #print('ffmpeg-encode:', time.time() - self.last_frame_input)

            mike_read_time += time.time() - t
            mike_nb_times += 1

            if mike_nb_times > 10:
                print('********** stream_video - wait', mike_wait_time/mike_nb_times)
                print('********** stream_video - read', mike_read_time/mike_nb_times)
                print('********** stream_video - loop', mike_back_time/mike_nb_times)
                mike_wait_time, mike_read_time, \
                mike_back_time, mike_nb_times  = 0, 0, 0, 0

            mike_back_date = time.time()

            yield (time.time(), out)
            #yield os.read(self.ffmpeg.stdout, 2048)

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

    def stream_video(self, width, height):
        streamer = Streamer(app=self, width=width, height=height)
        self.streamers.append(streamer)
        yield from streamer.stream_video()
        self.streamers.remove(streamer)

    def get_frame(self, unchanged):
        self.make_current()
        if not unchanged:
            self.display()  # really draw a new frame
        f = io.BytesIO()
        write_bmp(f, self.width, self.height)
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
