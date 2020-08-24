import numpy as np
from sakura.common.tools import iter_uniq
from sakura.common.exactness import EXACT, UNDEFINED
from sakura.common.pprint import pp_display_dataframe

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

# return
# *  -1 if a[<i>] < val
# *  0 if a[<i>] == val
# *  1 if a[<i>] > val
def np_array_cmp(a, val):
    return (a > val).astype(int) - (a < val).astype(int)

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
    def empty(size, dtype, exactness):
        chunk = np.ma.masked_array(np.empty(size, dtype)).view(NumpyChunk)
        chunk.exactness = exactness
        return chunk
    @staticmethod
    def check_missing_items(row, zero):
        for j, item in enumerate(row):
            if item is None:
                yield (zero[j], True)
            else:
                yield (item, False)
    @staticmethod
    def create(chunk_data, dtype, exactness):
        chunk = np.ma.empty(len(chunk_data), dtype)
        zero = np.zeros(1, dtype)[0]
        for i, row in enumerate(chunk_data):
            values, mask = tuple(zip(*NumpyChunk.check_missing_items(row, zero)))
            chunk[i] = values
            chunk.mask[i] = mask
        chunk = chunk.view(NumpyChunk)
        chunk.exactness = exactness
        return chunk
    def __getstate__(self):
        return (super().__getstate__(), self.exactness)
    def __setstate__(self, state):
        super().__setstate__(state[0])
        self.exactness = state[1]
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
            ordered_array = np.ma.array(self, ordered_dt, mask=self.mask).view(NumpyChunk)
            ordered_array.exactness = self.exactness
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
            new_data = new_data.view(NumpyChunk)
        else:
            # call base class method
            new_data = np.ma.MaskedArray.__getitem__(self, idx).view(NumpyChunk)
        new_data.exactness = self.exactness
        return new_data
    def __or__(self, right):
        # allow notation: left | right
        # we add columns of 'right' on the right of existing columns in left
        # ('left' and 'right' must have the same number of items)
        # again, we work around the fact np_paste_recarrays() does not work
        # directly on masked arrays.
        new_data = np_paste_recarrays(self.data, right.data).view(np.ma.MaskedArray)
        new_data.mask = np_paste_recarrays(self.mask, right.mask)
        new_data = new_data.view(NumpyChunk)
        new_data.exactness = min(self.exactness, right.exactness)
        return new_data
    def __gt__(self, other):
        if isinstance(other, tuple):
            # we want to filter rows strictly higher than the given tuple.
            # we must first compare first column, check if its higer, lower or equal.
            # if its equal, we have to check second column, etc.
            # to better use numpy optimizations, we attach a weight to columns
            # (4, 2, 1) for instance, and sum the result of the comparisons (-1, 0 or 1
            # multiplied by the weight).
            comp_table = np.zeros(len(self), dtype=int)
            coeffs = 1 << np.flip(np.arange(len(other)))
            for col, v, coeff in zip(self.columns, other, coeffs):
                comp_table += np_array_cmp(col, v) * coeff
            return comp_table > 0
        else:
            return super().__gt__(other)
    def exact(self):
        if self.exactness == UNDEFINED:
            raise Exception('Exactness of chunk has never been defined!')
        return self.exactness == EXACT
    def __array_finalize__(self, obj):
        super().__array_finalize__(obj)
        # if created from another NumpyChunk, propagate its exactness attribute
        # otherwise, set it to UNDEFINED.
        self.exactness = getattr(obj, 'exactness', UNDEFINED)
    def __repr__(self):
        if self.ndim == 0:
            # single row (as obtained by chunk[33] for instance)
            a = NumpyChunk.empty(1, self.dtype, self.exactness)
            a[0] = self
            return pp_display_dataframe(a)
        return pp_display_dataframe(self)
