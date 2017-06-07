import numpy as np
from itertools import islice
from sakura.daemon.processing.streams.output.base import OutputStreamBase
from sakura.common.chunk import NumpyChunk

DEFAULT_CHUNK_SIZE = 10000

class SimpleStream(OutputStreamBase):
    def __init__(self, label, compute_cb, columns=None):
        OutputStreamBase.__init__(self, label)
        self.compute_cb = compute_cb
        if columns is not None:
            for col in columns:
                self.add_column(col.label, col.type, col.tags)
    def __iter__(self):
        yield from self.compute_cb()
    def chunks(self, chunk_size = DEFAULT_CHUNK_SIZE, offset=0):
        dtype = self.get_dtype()
        it = islice(self.compute_cb(), offset, None)
        while True:
            chunk = np.fromiter(islice(it, chunk_size), dtype).view(NumpyChunk)
            if chunk.size == 0:
                break
            yield chunk
    def select_columns(self, *columns):
        indexes = list(col.index for col in columns)
        def filtered_compute_cb():
            for record in self.compute_cb():
                yield tuple(record[i] for i in indexes)
        return SimpleStream(self.label, filtered_compute_cb, columns)
    def filter(self, cond):
        col, comp_op, other = cond
        col_index = col.index
        def filtered_compute_cb():
            for record in self.compute_cb():
                if comp_op(record[col_index], other):
                    yield record
        return SimpleStream(self.label, filtered_compute_cb, self.columns)
