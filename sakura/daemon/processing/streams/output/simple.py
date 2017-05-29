import numpy as np
from itertools import islice
from sakura.daemon.processing.streams.output.base import OutputStreamBase

class SimpleStream(OutputStreamBase):
    def __init__(self, label, compute_cb):
        OutputStreamBase.__init__(self, label)
        self.compute_cb = compute_cb
    def __iter__(self):
        yield from self.compute_cb()
    def __iter_chunks__(self, chunk_size, offset=0):
        dtype = self.get_dtype()
        it = islice(self.compute_cb(), offset, None)
        while True:
            chunk = np.fromiter(islice(it, chunk_size), dtype).view(np.recarray)
            if chunk.size == 0:
                break
            yield chunk
