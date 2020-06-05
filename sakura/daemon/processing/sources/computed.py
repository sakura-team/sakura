import numpy as np
from enum import Enum
from itertools import islice
from sakura.daemon.processing.sources.base import SourceBase
from sakura.common.chunk import NumpyChunk, reassemble_chunk_stream

DEFAULT_CHUNK_SIZE = 10000

class ComputeMode(Enum):
    ITEMS = 0
    CHUNKS = 1

class ComputedSourceMixin:
    def work_from_filtered_dataset(self, array, chunk_size):
        if len(array) == 0:
            return
        if chunk_size is None:
            chunk_size = DEFAULT_CHUNK_SIZE
        # handle sorts
        array = np.sort(array, order=list(col._label for col in self.sort_columns))
        # handle offset
        if self._offset > 0:
            array = array[self._offset:]
        # handle limit
        if self._limit is not None:
            array = array[:self._limit]
        # handle column selection
        col_indexes = self.all_columns.get_indexes(self.columns)
        if col_indexes != tuple(range(len(self.all_columns))):
            # note: otherwise, all columns are selected, so the following is not useful
            array = array.view(NumpyChunk).__select_columns_indexes__(col_indexes)
        # handle chunk size
        for offset in range(0, len(array), chunk_size):
            yield array[offset:offset+chunk_size].view(NumpyChunk)

class ItemsComputedSource(SourceBase, ComputedSourceMixin):
    def __init__(self, label, compute_cb = None):
        SourceBase.__init__(self, label)
        self.data.compute_cb = compute_cb
    def chunks(self, chunk_size = DEFAULT_CHUNK_SIZE):
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
        # handle sorts
        if len(self.sort_columns) > 0:
            # unfortunately, we have no knowledge about the generated rows
            # so we have to compute the whole dataset before sorting it
            all_rows_list = list(it)
            native_dtype = self.get_native_dtype()
            array = np.empty(len(all_rows_list), native_dtype)
            if len(all_rows_list) > 0:
                for i, row in enumerate(all_rows_list):
                    array[i] = row
            # then work with this dataset
            yield from self.work_from_filtered_dataset(array, chunk_size)
            return
        # handle offset
        if self._offset > 0:
            it = islice(it, self._offset, None)
        # handle limit
        if self._limit is not None:
            it = islice(it, 0, self._limit)
        # handle column selection
        col_indexes = self.all_columns.get_indexes(self.columns)
        if col_indexes != tuple(range(len(self.all_columns))):
            # note: otherwise, all columns are selected, so the following is not useful
            def select_cols(it):
                for record in it:
                    yield tuple(record[i] for i in col_indexes)
            it = select_cols(it)
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

class ChunksComputedSource(SourceBase, ComputedSourceMixin):
    def __init__(self, label, compute_cb=None):
        SourceBase.__init__(self, label)
        self.data.compute_cb = compute_cb
    def chunks(self, chunk_size = None):
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
        # handle sorts
        if len(self.sort_columns) > 0:
            # unfortunately, we have no knowledge about the generated rows
            # so we have to compute the whole dataset before sorting it
            all_chunks = list(it)
            whole_len = sum(len(chunk) for chunk in all_chunks)
            if whole_len == 0:
                return
            array = np.empty(whole_len, all_chunks[0].dtype)
            off = 0
            for chunk in all_chunks:
                array[off:off+len(chunk)] = chunk
                off += len(chunk)
            # then work with this dataset
            yield from self.work_from_filtered_dataset(array, chunk_size)
            return
        # handle offset
        if self._offset > 0:
            def chunks_at_offset(it):
                curr_offset = 0
                for chunk in it:
                    discard = False
                    chunk_size = chunk.size
                    if self._offset > curr_offset:
                        chunk = chunk[self._offset-curr_offset:]
                        if chunk.size == 0:
                            discard = True
                    curr_offset += chunk_size
                    if not discard:
                        yield chunk
            it = chunks_at_offset(it)
        # handle limit
        if self._limit is not None:
            def chunks_up_to_limit(it):
                curr_offset = 0
                for chunk in it:
                    chunk_size = chunk.size
                    if curr_offset + chunk_size >= self._limit:
                        chunk = chunk[:self._limit-curr_offset]
                        if chunk.size > 0:
                            yield chunk  # last one
                        return
                    yield chunk
                    curr_offset += chunk_size
            it = chunks_up_to_limit(it)
        # handle column selection
        col_indexes = self.all_columns.get_indexes(self.columns)
        if col_indexes != tuple(range(len(self.all_columns))):
            # note: otherwise, all columns are selected, so the following is not useful
            def select_cols(it):
                for chunk in it:
                    yield chunk.view(NumpyChunk).__select_columns_indexes__(col_indexes)
            it = select_cols(it)
        # handle chunk_size
        it = reassemble_chunk_stream(it, self.get_dtype(), chunk_size)
        # output NumpyChunk elements
        for chunk in it:
            yield chunk.view(NumpyChunk)

def ComputedSource(label, compute_cb, compute_mode = ComputeMode.ITEMS):
    if compute_mode == ComputeMode.ITEMS:
        return ItemsComputedSource(label, compute_cb)
    else:
        return ChunksComputedSource(label, compute_cb)
