import gevent, shlex, time, gevent.os
from subprocess import Popen, PIPE
from gevent.queue import Queue, Empty
from gevent.socket import wait_read

# parameters of ffmpeg output video stream
# * FPS: frames per second
# * KEYFRAME_INTERVAL: caution not to increase this too much, because
#   it has an impact on the browser side (more data have to be buffered
#   in RAM)
FPS = 20
KEYFRAME_INTERVAL = 5
KEYFRAME_RATE = KEYFRAME_INTERVAL * FPS

FFMPEG_CMD_PATTERN = '''\
ffmpeg -f rawvideo -re -pix_fmt rgb24 -s %(width)dx%(height)d -max_delay 10000 -i - \
    -crf 24 -maxrate 1000k -bufsize 50k \
    -flush_packets 1 -tune zerolatency -vcodec libx264 -preset superfast -frag_duration 10000 -frag_size 1024 -vsync 1 \
    -filter:v fps=%(fps)d -vf vflip -g %(keyframe_rate)d -pix_fmt yuv420p -movflags +dash -max_delay 10000 -f mp4 - '''

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

    def stop(self):
        if self.ffmpeg is not None:
            ffmpeg = self.ffmpeg
            self.ffmpeg = None
            print('**** STREAMER BEING KILLED')
            ffmpeg.stdin.close()
            ffmpeg.wait()
            print('**** STREAMER KILLED')

    def __del__(self):
        self.stop()

    def stream_frames(self):
        last = None
        self.app.on_resize(self.width, self.height)
        while True:
            # in case we are both busy at inputting frames and at
            # reading ffmpeg output, favor the later
            gevent.idle()
            timed_out = False
            now = time.time()
            if last is None:
                timeout = 0
            else:
                # input frames according to FPS
                timeout = max(0.0, (last+ (1/FPS)) - now)
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
            yield self.app.get_frame(unchanged = timed_out)

    def feed_ffmpeg(self):
        try:
            fd = self.ffmpeg.stdin.fileno()
            for frame in self.stream_frames():
                gevent.os.write(fd, frame)
        except:
            return

    def stream_video(self):
        self.app.set_streamer_active(self)
        cmd = FFMPEG_CMD_PATTERN % dict(
                fps = FPS,
                keyframe_rate = KEYFRAME_RATE,
                width = self.width,
                height = self.height
        )
        self.ffmpeg = Popen(shlex.split(cmd), stdin=PIPE, stdout=PIPE, bufsize=0)
        gevent.Greenlet.spawn(self.feed_ffmpeg)
        while self.active:
            try:
                wait_read(self.ffmpeg.stdout.fileno(), timeout=1.0)
            except Exception as e:
                print(str(e))
                continue
            out = self.ffmpeg.stdout.read(8192)
            if len(out) == 0:
                break
            #print('chunk', len(out))
            yield out
