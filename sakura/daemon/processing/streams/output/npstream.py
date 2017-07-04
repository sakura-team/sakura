import numpy as np
from itertools import islice
from sakura.daemon.processing.streams.output.base import OutputStreamBase
from sakura.common.chunk import NumpyChunk

DEFAULT_CHUNK_SIZE = 100000

class NumpyArrayStream(OutputStreamBase):
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
    def __select_columns__(self, *col_indexes):
        col_labels = list(self.columns[col_index].label for col_index in col_indexes)
        filtered_array = self.array[col_labels]
        return NumpyArrayStream(self.label, filtered_array)
    def __filter__(self, col_index, comp_op, other):
        col_label = self.columns[col_index].label
        # we generate a condition of the form:
        # self.array[<col_label>] <comp_op> <other>
        # for example:
        # self.array['age'] > 20
        array_cond = comp_op(self.array[col_label], other)
        # then we apply this condition on the array
        return NumpyArrayStream(self.label, self.array[array_cond])
