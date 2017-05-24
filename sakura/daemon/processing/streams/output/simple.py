import numpy as np
from itertools import islice
from sakura.daemon.processing.tools import Registry
from sakura.daemon.processing.column import Column

class SimpleStream(Registry):
    def __init__(self, label, compute_cb):
        self.columns = []
        self.label = label
        self.compute_cb = compute_cb
        self.length = None
        self.last_iter_info = None
    def add_column(self, col_label, col_type, col_tags=()):
        return self.register(self.columns, Column,
                    col_label, col_type, tuple(col_tags),
                    self, len(self.columns))
    def get_info_serializable(self):
        return dict(label = self.label,
                    columns = [ col.get_info_serializable() for col in self.columns ],
                    length = self.length)
    def __iter__(self):
        for row in self.compute_cb():
            yield row
    def get_range(self, row_start, row_end):
        # try to reuse the last iterator if we scroll at the same offset
        # with same chunk size
        it = None
        if self.last_iter_info is not None:
            offset, chunk_size, last_it = self.last_iter_info
            if offset == row_start and chunk_size == row_end - row_start:
                it = last_it
        # otherwise, create a new iterator
        if it == None:
            it = self.__iter_chunks__(row_end-row_start, row_start)
        # read next chunk and return it
        for chunk in it:
            # update info about last iterator
            self.last_iter_info = row_start + chunk.size, row_end - row_start, it
            return chunk
        # if we are here, stream has ended, return empty range
        return np.empty((0,), self.get_dtype())
    def get_dtype(self):
        return np.dtype(list((col.label, col.type) for col in self.columns))
    def __iter_chunks__(self, chunk_size, offset=0):
        dtype = self.get_dtype()
        it = islice(self.compute_cb(), offset, None)
        while True:
            chunk = np.fromiter(islice(it, chunk_size), dtype).view(np.recarray)
            if chunk.size == 0:
                break
            yield chunk
