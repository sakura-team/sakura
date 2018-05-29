import numpy as np
from itertools import islice, count
from sakura.daemon.processing.streams.output.base import OutputStreamBase
from sakura.common.chunk import NumpyChunk

DEFAULT_CHUNK_SIZE = 100000

def iter_uniq(names):
    seen = set()
    for name in names:
        if name in seen:
            for i in count(start=2):
                alt_name = '%s(%d)' % (name, i)
                if alt_name not in seen:
                    name = alt_name
                    break
        seen.add(name)
        yield name

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
        # caution: we may have strange requests here, such
        # as building a stream with twice the same column
        # (e.g. XY plot with default value of axis selection
        # parameters)
        dt = self.array.dtype
        itemsize = dt.itemsize
        names = tuple(dt.names[i] for i in col_indexes)
        formats = [dt.fields[name][0] for name in names]
        offsets = [dt.fields[name][1] for name in names]
        names = tuple(iter_uniq(names))
        newdt = np.dtype(dict(names=names,
                              formats=formats,
                              offsets=offsets,
                              itemsize=itemsize))
        filtered_array = self.array.view(newdt)
        return NumpyArrayStream(self.label, filtered_array)
    def __filter__(self, col_index, comp_op, other):
        col_label = self.columns[col_index]._label
        # we generate a condition of the form:
        # self.array[<col_label>] <comp_op> <other>
        # for example:
        # self.array['age'] > 20
        array_cond = comp_op(self.array[col_label], other)
        # then we apply this condition on the array
        return NumpyArrayStream(self.label, self.array[array_cond])
