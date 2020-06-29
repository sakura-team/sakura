import numpy as np
from enum import Enum
from itertools import islice
from sakura.daemon.processing.sources.base import SourceBase
from sakura.daemon.processing.sort.progressive import progressive_sorted_chunks
from sakura.common.chunk import NumpyChunk
from sakura.common.stream import reassemble_chunk_stream, normalize_chunk_stream, \
                                 normalize_value_stream
from sakura.common.exactness import EXACT, APPROXIMATE, UNDEFINED

DEFAULT_CHUNK_SIZE = 10000

class ComputeMode(Enum):
    ITEMS = 0
    CHUNKS = 1

class ChunksComputedSource(SourceBase):
    def __init__(self, label, compute_cb=None):
        SourceBase.__init__(self, label)
        self.data.compute_cb = compute_cb
    def all_chunks(self, chunk_size = None):
        if len(self.sort_columns) > 0:
            # if we must sort:
            # - reinstanciate the source with only the row_filters
            # - stream chunks and apply a progressive sort algorithm on it
            # note: remaining steps are applied later
            source = self.reinstanciate()
            source.sort_columns = ()
            source._offset = 0
            source._limit = None
            it = progressive_sorted_chunks(source, self.sort_columns)
        else:
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
        # in both cases (sort involved or not), we apply remaining steps below:
        # offset, limit, column selection and reassembling.
        # handle offset
        if self._offset > 0:
            def chunks_at_offset(it):
                curr_offset = 0
                for chunk in it:
                    if self._offset > curr_offset:
                        chunk = chunk[self._offset-curr_offset:]
                    if chunk.size > 0:
                        if chunk.exact():
                            curr_offset += chunk.size
                        yield chunk
            it = chunks_at_offset(it)
        # handle limit
        if self._limit is not None:
            def chunks_up_to_limit(it):
                curr_offset = 0
                for chunk in it:
                    if curr_offset + chunk.size >= self._limit:
                        chunk = chunk[:self._limit-curr_offset]
                    if chunk.size > 0:
                        if chunk.exact():
                            curr_offset += chunk.size
                        yield chunk
                    if curr_offset == self._limit:
                        return
            it = chunks_up_to_limit(it)
        # handle column selection
        col_indexes = self.all_columns.get_indexes(self.columns)
        if col_indexes != tuple(range(len(self.all_columns))):
            # note: otherwise, all columns are selected, so the following is not useful
            def select_cols(it):
                for chunk in it:
                    yield chunk.view(NumpyChunk)[:,col_indexes]
            it = select_cols(it)
        # handle chunk_size
        it = reassemble_chunk_stream(it, self.get_dtype(), chunk_size)
        # output NumpyChunk elements
        for chunk in it:
            yield chunk.view(NumpyChunk)

class ItemsComputedSource:
    def __new__(cls, label, compute_cb):
        # we generate a compute function which will output chunks,
        # and build a ChunksComputedSource.
        chunks_source = None     # will be instanciated below
        def chunks_compute_cb():
            chunk_size = DEFAULT_CHUNK_SIZE
            it = compute_cb()
            dtype = chunks_source.get_dtype()
            # we may have "object" columns (e.g. storing strings of unknown length),
            # and np.fromiter() does not work in this case.
            exact_chunk = NumpyChunk.empty(chunk_size, dtype, EXACT)
            buf_level = 0
            for row, exactness in it:
                if exactness == EXACT:
                    exact_chunk[buf_level] = row
                    buf_level += 1
                    if buf_level == chunk_size:
                        yield exact_chunk
                        buf_level = 0
                else:   # approximate chunk
                    # yield a chunk of size 1
                    yield NumpyChunk.create([row], dtype, APPROXIMATE)
            if buf_level > 0:
                yield exact_chunk[:buf_level]   # last one
        chunks_source = ChunksComputedSource(label, chunks_compute_cb)
        return chunks_source

def ComputedSource(label, compute_cb, compute_mode = ComputeMode.ITEMS):
    if compute_mode == ComputeMode.ITEMS:
        def normalized_compute_cb():
            it = compute_cb()
            return normalize_value_stream(it)
        return ItemsComputedSource(label, normalized_compute_cb)
    else:
        def normalized_compute_cb():
            it = compute_cb()
            return normalize_chunk_stream(it)
        return ChunksComputedSource(label, normalized_compute_cb)
