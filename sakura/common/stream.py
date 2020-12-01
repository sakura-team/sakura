import numpy as np, gevent, traceback
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
        self._glet = None
        self._in_queue = Queue()
        self._out_queue = Queue()
    def __iter__(self):
        return self
    def __next__(self):
        if self._glet is None:
            self._spawn()
        self._in_queue.put(1)   # send chunk request
        try:
            res = self._out_queue.get(timeout = self._timeout)
        except Empty:
            return None
        if isinstance(res, Exception):
            raise res
        return res
    def _spawn(self):
        self._glet = gevent.spawn(self._run)
        self._out_queue.get() # wait for bg greenlet init
    def release(self):
        if self._glet is not None:
            self._glet.kill()   # kill
            self._in_queue = None
            self._out_queue = None
            self._glet = None
            self._it = None
    def _run(self):
        in_queue = self._in_queue
        out_queue = self._out_queue
        it = self._it
        try:
            # notify caller we are now running
            out_queue.put(1)
            # run main loop
            while True:
                # wait for next chunk request
                in_queue.get()
                # get next chunk and pass it to requester
                try:
                    chunk = next(it)
                    out_queue.put(chunk)
                except gevent.GreenletExit:
                    raise   # end
                except StopIteration as e:
                    out_queue.put(e)
                    return  # exit
                except Exception as e:
                    traceback.print_exc()
                    out_queue.put(e)
                    return  # exit
        except gevent.GreenletExit:
            raise   # end

# if delay between two chunks reaches timeout,
# yield a None value.
def apply_hard_timer_to_stream(it, timeout):
    return HardTimerIterator(it, timeout)
