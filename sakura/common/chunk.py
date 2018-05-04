import numpy as np

# properties are computed when they are accessed;
# as a result we do not have to deal with
# the complexity of ndarray subclass initialization.

def NumpyChunkColumn(col_name):
    class NumpyChunkColumn(np.ma.MaskedArray):
        @property
        def name(self):
            return col_name
    return NumpyChunkColumn

class NumpyChunk(np.ma.MaskedArray):
    @property
    def columns(self):
        return tuple(self[col_name].view(NumpyChunkColumn(col_name))
                    for col_name in self.dtype.names)
    @staticmethod
    def empty(dtype):
        return np.ma.masked_array(np.empty(0, dtype)).view(NumpyChunk)
    @staticmethod
    def create(chunk_data, dtype):
        row_list = list(tuple(row) for row in chunk_data)
        try:
            # fast path, if possible
            return np.ma.array(row_list, dtype).view(NumpyChunk)
        except TypeError:
            # error probably means we have missing values
            pass    # continue below
        # create a mask array indicating where values are None
        mask_dtype = np.ma.make_mask_descr(dtype)
        mask = np.ma.masked_equal(row_list, None).mask.view(mask_dtype).reshape(len(row_list))
        # copy chunk data in an array where column types are all set to "object" (=> allow None)
        obj_dtype = np.dtype(list((name, 'O') for name in dtype.names))
        obj_chunk = np.ma.array(row_list, obj_dtype, mask=mask)
        # create an empty chunk with appropriate type and copy unmasked data there
        chunk = np.ma.masked_array(np.empty(len(row_list), dtype), mask=mask)
        for colname in dtype.names:
            colmask = ~obj_chunk[colname].mask
            chunk[colname][colmask] = obj_chunk[colname][colmask]
        return chunk.view(NumpyChunk)

