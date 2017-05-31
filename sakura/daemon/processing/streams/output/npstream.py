import numpy as np
from itertools import islice
from sakura.daemon.processing.streams.output.base import OutputStreamBase

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
            yield self.array[offset:offset+chunk_size].view(np.recarray)
            offset += chunk_size
