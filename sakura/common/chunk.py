import numpy as np

# properties are computed when they are accessed;
# as a result we do not have to deal with
# the complexity of ndarray subclass initialization.

class NumpyChunkColumn(np.ma.MaskedArray):
    @property
    def name(self):
        return self.col_name
    def __get_state__(self):
        return (np.ma.MaskedArray.__get_state__(self), self.col_name)
    def __set_state__(self, st):
        ma_st, col_name = st
        self.col_name = col_name
        return np.ma.MaskedArray.__set_state__(self, ma_st)

class NumpyChunk(np.ma.MaskedArray):
    def get_column(self, col_name):
        col = self[col_name].view(NumpyChunkColumn)
        col.col_name = col_name
        return col
    @property
    def columns(self):
        return tuple(self.get_column(col_name)
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
    def __reduce__(self):
        # workaround for numpy.ma.masked_array failing to deserialize
        # when we have overlapping or out-of-order fields
        # (i.e. when self.dtype shows itemsize and offsets info).
        try:
            # deserialization code tries to read this attribute,
            # which fails in this specific case.
            self.dtype.descr
            # ok, no problem, use standard method:
            return np.ma.MaskedArray.__reduce__(self)
        except ValueError:
            # error case detected.
            # we will have to copy the array into one with ordered fields.
            names = self.dtype.names
            formats = tuple(self.dtype.fields[n][0] for n in names)
            ordered_dt = np.dtype(dict(names=names, formats=formats))
            ordered_array = np.ma.array(self, ordered_dt, mask=self.mask)
            return np.ma.MaskedArray.__reduce__(ordered_array)
