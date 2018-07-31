import numpy as np
from sakura.daemon.processing.sources.base import SourceBase
from sakura.common.chunk import NumpyChunk

DEFAULT_CHUNK_SIZE = 100000

class NumpyArraySource(SourceBase):
    def __init__(self, label, array, rows_cond = None):
        SourceBase.__init__(self, label)
        self.array = array
        for col_label in array.dtype.names:
            col_type = array.dtype[col_label]
            self.add_column(col_label, col_type)
        self.rows_cond = rows_cond
    def __iter__(self):
        for chunk in self.chunks():
            yield from chunk
    def chunks(self, chunk_size = DEFAULT_CHUNK_SIZE, offset=0):
        if self.rows_cond is None:
            # iterate over all rows
            while offset < self.array.size:
                yield self.array[offset:offset+chunk_size].view(NumpyChunk)
                offset += chunk_size
        else:
            # iterate over selected rows
            indices = self.rows_cond.nonzero()[0]
            while offset < indices.size:
                yield self.array[indices[offset:offset+chunk_size]].view(NumpyChunk)
                offset += chunk_size
    def __select_columns__(self, *col_indexes):
        filtered_array = self.array.view(NumpyChunk).__select_columns__(*col_indexes)
        return NumpyArraySource(self.label, filtered_array)
    def __filter__(self, col_index, comp_op, other):
        col_label = self.columns[col_index]._label
        # we generate a condition of the form:
        # self.array[<col_label>] <comp_op> <other>
        # for example:
        # self.array['age'] > 20
        # The result of this expression is a table of booleans
        # indicating whether or not each row satisfies the condition.
        rows_cond = comp_op(self.array[col_label], other)
        # if we already add self.rows_cond, aggregate
        if self.rows_cond is not None:
            rows_cond = np.logical_and(rows_cond, self.rows_cond)
        # return filtered object
        return NumpyArraySource(self.label, self.array, rows_cond)
