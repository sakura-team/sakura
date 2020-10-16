import numpy as np, gevent
from gevent.queue import Queue, Empty
from sakura.common.release import auto_release
from sakura.common.chunk import NumpyChunk
from sakura.common.exactness import EXACT, APPROXIMATE, UNDEFINED, Exactness

def reassemble_chunk_stream(it, dt, chunk_size):
    if chunk_size is None:
        return it   # nothing to do
    def reassembled(it):
        buf_chunk = NumpyChunk.empty(chunk_size, dt, UNDEFINED)
        buf_level = 0
        for chunk in it:
            if chunk.exact():
                # depending on requested chunk_size, we may have to cut this
                # chunk into several parts.
                while chunk.size > 0:
                    chunk_part = chunk[:chunk_size-buf_level]
                    buf_chunk[buf_level:buf_level+chunk_part.size] = chunk_part
                    buf_level += chunk_part.size
                    if buf_level == chunk_size:
                        buf_chunk.exactness = EXACT
                        yield buf_chunk
                        buf_level = 0
                    chunk = chunk[chunk_part.size:]
            else:
                # size of approximate chunks is lower or equal to chunk_size.
                # we concatenate current exact rows of buf_chunk with approximate
                # ones of this chunk.
                chunk_part = chunk[:chunk_size-buf_level]
                buf_chunk[buf_level:buf_level+chunk_part.size] = chunk_part
                inexact_chunk = buf_chunk[:buf_level+chunk_part.size]
                inexact_chunk.exactness = APPROXIMATE
                yield inexact_chunk
        if buf_level > 0:
            # last exact chunk is the only one which may have a size lower than
            # chunk_size
            buf_chunk = buf_chunk[:buf_level]
            buf_chunk.exactness = EXACT
            yield buf_chunk
    return reassembled(it)

def normalize_chunk_stream(it):
    for chunk in it:
        chunk = chunk.view(NumpyChunk)
        # if not specified we consider the chunk is exact
        if chunk.exactness == UNDEFINED:
            chunk.exactness = EXACT
        yield chunk

def normalize_value_stream(it):
    for val in it:
        # if not specified we consider the value is exact
        if isinstance(val, tuple) and len(val) == 2 and isinstance(val[1], Exactness):
            yield val   # val is already a tuple (<row>, <exactness>)
        else:
            yield val, EXACT

@auto_release
class HardTimerIterator:
    def __init__(self, it, timeout):
        self._it = it
        self._timeout = timeout
        self._greenlet = None
        self._in_queue = Queue()
        self._out_queue = Queue()
    def __iter__(self):
        return self
    def __next__(self):
        if self._greenlet is None:
            self._spawn()
        if self._out_queue.qsize() == 0:
            if self._in_queue.qsize() == 0:
                # we enqueue two tokens to be able to check
                # background greenlet status
                self._in_queue.put(1)
                self._in_queue.put(1)   # second token
        try:
            res = self._out_queue.get(timeout = self._timeout)
        except Empty:
            return None
        if isinstance(res, Exception):
            raise res
        return res
    def _spawn(self):
        self._greenlet = gevent.spawn(self._run)
    def release(self):
        if self._greenlet is not None:
            if self._in_queue.qsize() == 0:
                self._in_queue.put(0)   # gentle stop request
            else:
                # greenlet is blocked in next(it)
                self._greenlet.kill()   # kill
            self._in_queue = None
            self._out_queue = None
            self._greenlet = None
            self._it = None
    def _run(self):
        in_queue = self._in_queue
        out_queue = self._out_queue
        it = self._it
        while True:
            action = in_queue.get()
            if action == 0:
                break   # end
            else:
                try:
                    chunk = next(it)
                    # retrieve the second token
                    # (let the main greenlet know we are not blocked on next(it) any more)
                    in_queue.get()  # second token
                    out_queue.put(chunk)
                except gevent.GreenletExit:
                    break   # end
                except Exception as e:
                    in_queue.get()  # second token
                    out_queue.put(e)

# if delay between two chunks reaches timeout,
# yield a None value.
def apply_hard_timer_to_stream(it, timeout):
    return HardTimerIterator(it, timeout)
