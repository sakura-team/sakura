import numpy as np
from enum import Enum
from itertools import islice
from sakura.daemon.processing.sources.base import SourceBase
from sakura.common.chunk import NumpyChunk

DEFAULT_CHUNK_SIZE = 10000

class ComputeMode(Enum):
    ITEMS = 0
    CHUNKS = 1

class ItemsComputedSource(SourceBase):
    def __init__(self, label, compute_cb, columns=None):
        SourceBase.__init__(self, label)
        self.compute_cb = compute_cb
        if columns is not None:
            for col in columns:
                self.add_column(col._label, col._type, col._tags)
    def __iter__(self):
        yield from self.compute_cb()
    def chunks(self, chunk_size = DEFAULT_CHUNK_SIZE, offset=0):
        dtype = self.get_dtype()
        it = islice(self.compute_cb(), offset, None)
        while True:
            # we may have "object" columns (e.g. storing strings of unknown length),
            # and np.fromiter() does not work in this case.
            chunk = np.empty(chunk_size, dtype)
            i = -1
            for i, row in enumerate(islice(it, chunk_size)):
                chunk[i] = row
            if i == -1:
                break
            yield chunk[:i+1].view(NumpyChunk)
    def __select_columns__(self, *col_indexes):
        def filtered_compute_cb():
            for record in self.compute_cb():
                yield tuple(record[i] for i in col_indexes)
        columns = tuple(self.columns[i] for i in col_indexes)
        return ItemsComputedSource(self.label, filtered_compute_cb, columns)
    def __filter__(self, col_index, comp_op, other):
        def filtered_compute_cb():
            for record in self.compute_cb():
                if comp_op(record[col_index], other):
                    yield record
        return ItemsComputedSource(self.label, filtered_compute_cb, self.columns)

class ChunksComputedSource(SourceBase):
    def __init__(self, label, compute_cb, columns=None):
        SourceBase.__init__(self, label)
        self.compute_cb = compute_cb
        if columns is not None:
            for col in columns:
                self.add_column(col._label, col._type, col._tags)
    def __iter__(self):
        for chunk in self.chunks():
            yield from chunk
    def chunks_at_offset(self, offset=0):
        if offset == 0:
            yield from self.compute_cb()
        else:
            curr_offset = 0
            for chunk in self.compute_cb():
                discard = False
                chunk_size = chunk.size
                if offset > curr_offset:
                    chunk = chunk[offset-curr_offset:]
                    if chunk.size == 0:
                        discard = True
                curr_offset += chunk_size
                if not discard:
                    yield chunk
    def chunks(self, chunk_size = None, offset=0):
        requested_chunk_size = chunk_size
        if requested_chunk_size == None:
            for chunk in self.chunks_at_offset(offset):
                yield chunk.view(NumpyChunk)
        else:
            # ensure we output chunks of the expected size
            buf_chunk = np.empty(requested_chunk_size, self.get_dtype())
            buf_level = 0
            for chunk in self.chunks_at_offset(offset):
                while chunk.size > 0:
                    chunk_part = chunk[:requested_chunk_size-buf_level]
                    buf_chunk[buf_level:buf_level+chunk_part.size] = chunk_part
                    buf_level += chunk_part.size
                    if buf_level == requested_chunk_size:
                        yield buf_chunk.view(NumpyChunk)
                        buf_level = 0
                    chunk = chunk[chunk_part.size:]
            if buf_level > 0:
                buf_chunk = buf_chunk[:buf_level]
                yield buf_chunk.view(NumpyChunk)
    def __select_columns__(self, *col_indexes):
        def filtered_compute_cb():
            for chunk in self.compute_cb():
                yield chunk.view(NumpyChunk).__select_columns__(*col_indexes)
        columns = tuple(self.columns[i] for i in col_indexes)
        return ChunksComputedSource(self.label, filtered_compute_cb, columns)
    def __filter__(self, col_index, comp_op, other):
        col_label = self.columns[col_index]._label
        def filtered_compute_cb():
            for chunk in self.compute_cb():
                chunk_cond = comp_op(chunk[col_label], other)
                chunk = chunk[chunk_cond]
                if chunk.size > 0:
                    yield chunk
        return ChunksComputedSource(self.label, filtered_compute_cb, self.columns)
    def create_chunk(self, array):
        return NumpyChunk(array, self.get_dtype())

def ComputedSource(label, compute_cb, compute_mode = ComputeMode.ITEMS, columns=None):
    if compute_mode == ComputeMode.ITEMS:
        return ItemsComputedSource(label, compute_cb, columns)
    else:
        return ChunksComputedSource(label, compute_cb, columns)
