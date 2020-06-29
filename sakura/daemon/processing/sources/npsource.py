import numpy as np
from sakura.daemon.processing.sources.base import SourceBase
from sakura.common.chunk import NumpyChunk
from sakura.common.types import np_dtype_to_sakura_type
from sakura.common.exactness import EXACT

DEFAULT_CHUNK_SIZE = 100000

class NumpyArraySource(SourceBase):
    def __init__(self, label, array = None):
        SourceBase.__init__(self, label)
        if array is not None:
            self.data.array = array
            for col_label in array.dtype.names:
                col_dt = array.dtype[col_label]
                col_type, col_type_params = np_dtype_to_sakura_type(col_dt)
                self.add_column(col_label, col_type, **col_type_params)
    def all_chunks(self, chunk_size = None):
        if chunk_size is None:
            chunk_size = DEFAULT_CHUNK_SIZE
        array = self.data.array
        # apply row filters if any
        if len(self.row_filters) > 0:
            # select appropriate row indices
            row_indices = None  # all indices for now
            for col, comp_op, other in self.row_filters:
                array_col = array[col._label]
                if row_indices is not None:
                    array_col = array_col[row_indices]  # keep only the indices that passed prev filters
                # with numpy, the result of an expression like
                # <array> > 20
                # is a table of booleans indicating whether or not each row
                # satisfies the condition.
                booleans = comp_op(array_col, other)
                # applying nonzero()[0] gives the position where the booleans are True
                new_indices = booleans.nonzero()[0]
                # translate back the new indices in original numbering
                if row_indices is None:
                    row_indices = new_indices
                else:
                    row_indices = row_indices[new_indices]
            array = array[row_indices]
        # apply optional sort
        if len(self.sort_columns) > 0:
            array = np.sort(array, order=list(col._label for col in self.sort_columns))
        # apply limit and offset
        if self._limit is not None:
            array = array[self._offset:self._offset+self._limit]
        elif self._offset > 0:
            array = array[self._offset:]
        # only keep selected columns
        col_indexes = self.all_columns.get_indexes(self.columns)
        array = array.view(NumpyChunk)[:,col_indexes]
        # iterate over resulting rows
        offset = 0
        while offset < array.size:
            chunk = array[offset:offset+chunk_size].view(NumpyChunk)
            chunk.exactness = EXACT
            yield chunk
            offset += chunk_size
