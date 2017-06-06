import numpy as np
from itertools import islice
from sakura.daemon.processing.streams.output.base import OutputStreamBase
from sakura.common.chunk import NumpyChunk

DEFAULT_CHUNK_SIZE = 100000

class NumpyStream(OutputStreamBase):
    def __init__(self, label, array):
        OutputStreamBase.__init__(self, label)
        self.array = array
        for col_label in array.dtype.names:
            col_type = array.dtype[col_label]
            self.add_column(col_label, col_type)
    def __iter__(self):
        yield from self.array
    def chunks(self, chunk_size = DEFAULT_CHUNK_SIZE, offset=0):
        while offset < self.array.size:
            yield self.array[offset:offset+chunk_size].view(NumpyChunk)
            offset += chunk_size
    def select_columns(self, *columns):
        filtered_array = self.array[list(col.label for col in columns)]
        return NumpyStream(self.label, filtered_array)
    def filter(self, cond):
        col, comp_op, other = cond
        # we generate a condition of the form:
        # self.array[<col_label>] <comp_op> <other>
        # for example:
        # self.array['age'] > 20
        array_cond = comp_op(self.array[col.label], other)
        # then we apply this condition on the array
        return NumpyStream(self.label, self.array[array_cond])
