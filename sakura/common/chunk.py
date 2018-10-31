import numpy as np
from itertools import count

# iterate over "names" ensuring they are all different.
# if 2 names match, add suffix "(2)", then "(3)", etc.
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

def np_select_columns(array, col_indexes):
    # caution: we may have strange requests here, such
    # as building a stream with twice the same column
    # (e.g. XY plot with default value of axis selection
    # parameters)
    dt = array.dtype
    itemsize = dt.itemsize
    names = tuple(dt.names[i] for i in col_indexes)
    formats = [dt.fields[name][0] for name in names]
    offsets = [dt.fields[name][1] for name in names]
    names = tuple(iter_uniq(names))
    newdt = np.dtype(dict(names=names,
                          formats=formats,
                          offsets=offsets,
                          itemsize=itemsize))
    return array.view(newdt)

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
    def check_missing_items(row, zero):
        for j, item in enumerate(row):
            if item is None:
                yield (zero[j], True)
            else:
                yield (item, False)
    @staticmethod
    def create(chunk_data, dtype):
        chunk = np.ma.empty(len(chunk_data), dtype)
        zero = np.zeros(1, dtype)[0]
        for i, row in enumerate(chunk_data):
            values, mask = tuple(zip(*NumpyChunk.check_missing_items(row, zero)))
            chunk[i] = values
            chunk.mask[i] = mask
        return chunk.view(NumpyChunk)
    def __reduce__(self):
        # workaround for numpy.ma.masked_array failing to deserialize
        # when we have overlapping or out-of-order fields
        # (i.e. when self.dtype shows itemsize and offsets info).
        try:
            # deserialization code tries to read self.dtype.descr,
            # which may throw ValueError in this specific case.
            # another error case can be detected by comparing
            # the 2 following lengths.
            if len(self.dtype.descr) != len(self.dtype.fields):
                raise ValueError
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
    def __select_columns__(self, *col_indexes):
        # workaround the fact np_select_columns() does not work directly
        # on masked arrays.
        new_data = np_select_columns(self.data, col_indexes).view(np.ma.MaskedArray)
        new_data.mask = np_select_columns(self.mask, col_indexes)
        return new_data.view(NumpyChunk)
