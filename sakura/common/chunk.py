import numpy as np
from sakura.common.tools import iter_uniq

def np_compact_dtype(dt):
    # recompute offsets to make dtype more compact
    return np.dtype([(name, info[0]) for name, info in dt.fields.items()])

def np_select_columns(array, col_indexes):
    # caution: we may have strange requests here, such
    # as building a stream with twice the same column
    # (e.g. XY plot with default value of axis selection
    # parameters)
    dt = array.dtype
    itemsize = dt.itemsize
    orig_names = tuple(dt.names[i] for i in col_indexes)
    formats = [dt.fields[name][0] for name in orig_names]
    offsets = [dt.fields[name][1] for name in orig_names]
    names = tuple(iter_uniq(orig_names))
    newdt = np.dtype(dict(names=names,
                          formats=formats,
                          offsets=offsets,
                          itemsize=itemsize))
    # numpy disallows viewing a recarray with a different dtype
    # if it contains object columns.
    try:
        return array.view(newdt)
    except TypeError:
        pass    # continue below
    # as a fallback, return a new array instead of a view.
    newdt = np_compact_dtype(newdt)
    new_array = np.empty(len(array), dtype=newdt)
    for orig_name, name in zip(orig_names, names):
        new_array[name] = array[orig_name]
    return new_array

def np_paste_recarrays(a1, a2):
    """allows to 'join' two structured arrays, i.e. paste columns
       of a2 on the right of existing columns in a1"""
    # compute dtype in a robust way
    n = len(a1)
    joint_itemsize = a1.itemsize + a2.itemsize
    a1_names, a2_names = tuple(a1.dtype.names), tuple(a2.dtype.names)
    names = tuple(iter_uniq(a1_names + a2_names))
    a1_formats, a1_offsets = zip(*(a1.dtype.fields[name][0:2] for name in a1_names))
    a2_formats, a2_offsets = zip(*(a2.dtype.fields[name][0:2] for name in a2_names))
    newdt = np.dtype(dict(  names = names,
                          formats = a1_formats + a2_formats,
                          offsets = a1_offsets + tuple((off + a1.itemsize) for off in a2_offsets),
                         itemsize = joint_itemsize))
    # numpy disallows viewing a recarray with a different dtype
    # if it contains object columns.
    if not a1.dtype.hasobject and not a2.dtype.hasobject:
        # no objects, we can go fast
        # compute resulting array by viewing it as a 2D array of bytes
        # idea from https://stackoverflow.com/a/5355974
        joint = np.empty((n, joint_itemsize), dtype=np.uint8)
        joint[:,0:a1.itemsize] = a1.view(np.uint8).reshape(n,a1.itemsize)
        joint[:,a1.itemsize:joint_itemsize] = a2.view(np.uint8).reshape(n,a2.itemsize)
        return joint.ravel().view(newdt)
    else:
        # just copy columns
        newdt = np_compact_dtype(newdt)
        orig_names = a1_names + a2_names
        orig_arrays = [ a1 ] * len(a1_names) + [ a2 ] * len(a2_names)
        new_array = np.empty(n, dtype=newdt)
        for orig_name, orig_array, name in zip(orig_names, orig_arrays, names):
            new_array[name] = orig_array[orig_name]
        return new_array

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
    def __getitem__(self, idx):
        if isinstance(idx, tuple) and len(idx) == 2:
            # allow notation: chunk[<rows>,<cols>]
            rows, col_indices = idx
            sub_chunk = self[rows]
            # workaround the fact np_select_columns() does not work directly
            # on masked arrays.
            new_data = np_select_columns(sub_chunk.data, col_indices).view(np.ma.MaskedArray)
            new_data.mask = np_select_columns(sub_chunk.mask, col_indices)
            return new_data.view(NumpyChunk)
        else:
            # call base class method
            return np.ma.MaskedArray.__getitem__(self, idx).view(NumpyChunk)
    def __paste_right__(self, right):
        # add columns of 'right' on the right of existing columns in self
        # ('self' and 'right' must have the same number of items)
        # again, we work around the fact np_paste_recarrays() does not work
        # directly on masked arrays.
        new_data = np_paste_recarrays(self.data, right.data).view(np.ma.MaskedArray)
        new_data.mask = np_paste_recarrays(self.mask, right.mask)
        return new_data.view(NumpyChunk)

def reassemble_chunk_stream(it, dt, chunk_size):
    if chunk_size is None:
        return it   # nothing to do
    def reassembled(it):
        buf_chunk = np.empty(chunk_size, dt)
        buf_level = 0
        for chunk in it:
            while chunk.size > 0:
                chunk_part = chunk[:chunk_size-buf_level]
                buf_chunk[buf_level:buf_level+chunk_part.size] = chunk_part
                buf_level += chunk_part.size
                if buf_level == chunk_size:
                    yield buf_chunk.view(NumpyChunk)
                    buf_level = 0
                chunk = chunk[chunk_part.size:]
        if buf_level > 0:
            buf_chunk = buf_chunk[:buf_level]
            yield buf_chunk.view(NumpyChunk)
    return reassembled(it)
