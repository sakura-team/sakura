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
    def __init__(self, label, compute_cb = None):
        SourceBase.__init__(self, label)
        self.data.compute_cb = compute_cb
    def chunks(self, chunk_size = DEFAULT_CHUNK_SIZE, offset=0):
        it = self.data.compute_cb()
        # handle filters
        if len(self.row_filters) > 0:
            indexed_filters = tuple((self.all_columns.get_index(col), comp_op, other) \
                                for col, comp_op, other in self.row_filters)
            def filter_rows(it):
                for record in it:
                    for col_index, comp_op, other in indexed_filters:
                        if comp_op(record[col_index], other):
                            yield record
            it = filter_rows(it)
        # handle column selection
        col_indexes = self.all_columns.get_indexes(self.columns)
        if col_indexes != tuple(range(len(self.all_columns))):
            # note: otherwise, all columns are selected, so the following is not useful
            def select_cols(it):
                for record in it:
                    yield tuple(record[i] for i in col_indexes)
            it = select_cols(it)
        # handle offset
        it = islice(it, offset, None)
        # handle chunk size
        dtype = self.get_dtype()
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

class ChunksComputedSource(SourceBase):
    def __init__(self, label, compute_cb=None):
        SourceBase.__init__(self, label)
        self.data.compute_cb = compute_cb
    def chunks(self, chunk_size = None, offset=0):
        it = self.data.compute_cb()
        # handle filters
        if len(self.row_filters) > 0:
            def filter_rows(it):
                for chunk in it:
                    for col, comp_op, other in self.row_filters:
                        chunk_cond = comp_op(chunk[col._label], other)
                        chunk = chunk[chunk_cond]
                        if chunk.size == 0:
                            break
                    if chunk.size > 0:
                        yield chunk
            it = filter_rows(it)
        # handle column selection
        col_indexes = self.all_columns.get_indexes(self.columns)
        if col_indexes != tuple(range(len(self.all_columns))):
            # note: otherwise, all columns are selected, so the following is not useful
            def select_cols(it):
                for chunk in it:
                    yield chunk.view(NumpyChunk).__select_columns_indexes__(col_indexes)
            it = select_cols(it)
        # handle offset
        if offset > 0:
            def chunks_at_offset(it):
                curr_offset = 0
                for chunk in it:
                    discard = False
                    chunk_size = chunk.size
                    if offset > curr_offset:
                        chunk = chunk[offset-curr_offset:]
                        if chunk.size == 0:
                            discard = True
                    curr_offset += chunk_size
                    if not discard:
                        yield chunk
            it = chunks_at_offset(it)
        # handle chunk_size
        requested_chunk_size = chunk_size
        if requested_chunk_size is not None:
            # ensure we output chunks of the expected size
            def reassembled(it):
                buf_chunk = np.empty(requested_chunk_size, self.get_dtype())
                buf_level = 0
                for chunk in it:
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
            it = reassembled(it)
        # output NumpyChunk elements
        for chunk in it:
            yield chunk.view(NumpyChunk)

def ComputedSource(label, compute_cb, compute_mode = ComputeMode.ITEMS):
    if compute_mode == ComputeMode.ITEMS:
        return ItemsComputedSource(label, compute_cb)
    else:
        return ChunksComputedSource(label, compute_cb)
