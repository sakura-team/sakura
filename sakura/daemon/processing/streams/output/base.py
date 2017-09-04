import numpy as np
from sakura.common.chunk import NumpyChunk
from sakura.daemon.processing.tools import Registry
from sakura.daemon.processing.cache import Cache
from sakura.daemon.processing.column import Column

class OutputStreamBase(Registry):
    def __init__(self, label):
        self.columns = []
        self.label = label
        self.length = None
        self.range_iter_cache = Cache(10)
    def add_column(self, col_label, col_type, col_tags=()):
        return self.register(self.columns, Column,
                    col_label, col_type, tuple(col_tags),
                    self, len(self.columns))
    def pack(self):
        return dict(label = self.label,
                    columns = self.columns,
                    length = self.length)
    def get_range(self, row_start, row_end, columns=None, filters=()):
        chunk_len = row_end-row_start
        # try to reuse the last iterator
        it = self.range_iter_cache.get(row_start, row_end, columns, filters)
        in_cache = it is not None
        # otherwise, create a new iterator
        if not in_cache:
            stream = self
            if columns is not None:
                stream = stream.select_columns(*columns)
            for condition in filters:
                stream = stream.filter(condition)
            it = stream.chunks(chunk_len, row_start)
        # read next chunk and return it
        for chunk in it:
            # update info about last iterator
            new_row_start = row_start + chunk.size
            self.range_iter_cache.save(it,
                new_row_start, new_row_start + chunk_len, columns, filters)
            return chunk
        # if we are here, stream has ended, forget about iterator and
        # return empty chunk
        if in_cache:
            self.range_iter_cache.forget(it)
        return NumpyChunk(0, self.get_dtype())
    def get_dtype(self):
        return np.dtype(list(col.get_dtype() for col in self.columns))
    def select_columns(self, *columns):
        # verify that at least 1 column is specified
        if len(columns) == 0:
            return self
        # column objects or indices are accepted
        if isinstance(columns[0], int):
            col_indexes = tuple(columns)
        else:
            col_indexes = tuple(col.index for col in columns)
        # if all columns are selected in the same order, return self...
        if col_indexes == tuple(range(len(self.columns))):
            return self
        # compute a substream
        return self.__select_columns__(*col_indexes)
    def filter(self, cond):
        col, comp_op, other = cond
        # column object or index are accepted
        if isinstance(col, int):
            col_index = col
        else:
            col_index = col.index
        # compute a substream
        return self.__filter__(col_index, comp_op, other)
