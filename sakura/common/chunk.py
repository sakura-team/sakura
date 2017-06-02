import numpy as np

# properties are computed when they are accessed;
# as a result we do not have to deal with
# the complexity of ndarray subclass initialization.

def NumpyChunkColumn(col_name):
    class NumpyChunkColumn(np.ndarray):
        @property
        def name(self):
            return col_name
    return NumpyChunkColumn

class NumpyChunk(np.ndarray):
    @property
    def columns(self):
        return tuple(self[col_name].view(NumpyChunkColumn(col_name))
                    for col_name in self.dtype.names)

