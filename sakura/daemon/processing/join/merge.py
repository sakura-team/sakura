import numpy as np
from sakura.common.chunk import NumpyChunk
from sakura.daemon.processing.sources.types import SourceTypes

# merge join algorithm implementation:
# sort left and right side, then merge.

# let us consider the following example:
#
# a = np.array([ (2,'a'),
#                (2,'b'),
#                (7,'c'),
#                (8,'d'),
#                (10,'e'),
#                (10,'f'),
#                (10,'g'),
#                (11,'h'),
#                (11,'i')], dtype=[('i', int), ('s', object)])
#
# b = np.array([ (5,'Z'),
#                (8,'A'),
#                (8,'B'),
#                (9,'C'),
#                (10,'D'),
#                (10,'E'),
#                (13,'F')], dtype=[('i', int), ('s', object)])
#
# we want to join columns a['i'] and b['i'].
#
# common values are:
# * 8  (1 element on left, 2 elements on right)
# * 10 (3 elements on left, 2 elements on right)
#
# for all common values, we must apply a cartesian product
# in order to get all possible pairs of elements.
#
# in this example, function get_join_indices() below should return the
# following indices:
# on the left:  [ 3, 3, 4, 5, 6, 4, 5, 6 ]
# on the right: [ 1, 2, 4, 4, 4, 5, 5, 5 ]

def merge_right_indices(left, right):
    # prevent possible out of bound case:
    # without this, last index in right_in_left_insert_idx might be len(left),
    # which would cause an error when computing left[right_in_left_insert_idx].
    # we cannot have several values higher than left[-1] at the end of right,
    # because of strictly increasing values, and the fact we previously reduced
    # left and right to intersection of their min-max interval.
    if right[-1] > left[-1]:
        right = right[:-1]
    # compute right in left insert indices
    right_in_left_insert_idx = np.searchsorted(left, right)
    # compute right indices
    right_booleans = (right == left[right_in_left_insert_idx])
    right_indices = right_booleans.nonzero()[0]
    return right_indices

def merge_left_indices(left, right):
    return merge_right_indices(right, left)

# reduce vector v to values in the given interval
# return offset and section of v
def reduce_min_max(v, min_val, max_val):
    v_idx_min, v_idx_max = np.searchsorted(v, (min_val, max_val))
    if v_idx_max < len(v) and v[v_idx_max] == max_val:
        v_idx_max += 1
    return v_idx_min, v[v_idx_min:v_idx_max]

# return indices of common values
def merge_indices(left, right):
    # first, reduce chunks to intersection of their min-max interval
    right_offset, right = reduce_min_max(right, left[0], left[-1])
    if len(right) == 0:
        return None, None
    left_offset, left = reduce_min_max(left, right[0], right[-1])
    if len(left) == 0:
        return None, None
    # check which way will be more efficient
    if len(left) > len(right):
        right_indices = merge_right_indices(left, right)
        if len(right_indices) == 0:
            return None, None
        right = right[right_indices]
        offset, left = reduce_min_max(left, right[0], right[-1])
        left_offset += offset
        if len(left) == 0:
            return None, None
        left_indices = merge_left_indices(left, right)
    else:
        left_indices = merge_left_indices(left, right)
        if len(left_indices) == 0:
            return None, None
        left = left[left_indices]
        offset, right = reduce_min_max(right, left[0], left[-1])
        right_offset += offset
        if len(right) == 0:
            return None, None
        right_indices = merge_right_indices(left, right)
    # return
    return left_indices + left_offset, right_indices + right_offset

# ensure that repeated values do not span accross several chunks
def fix_spanning_repeated_values(it):
    prev_chunk = None
    for chunk in it:
        if prev_chunk is None:
            prev_chunk = chunk
            continue
        if chunk[0][0] != prev_chunk[-1][0]:
            yield prev_chunk
            prev_chunk = chunk
            continue
        # same value
        new_chunk = np.ma.empty(len(prev_chunk) + len(chunk), chunk.dtype)
        new_chunk[0:len(prev_chunk)] = prev_chunk
        new_chunk[len(prev_chunk):] = chunk
        prev_chunk = new_chunk.view(NumpyChunk)
        continue
    if prev_chunk is not None:
        yield prev_chunk

# return the first index of each unique value in sorted vector v
# note: we also add the length as the last element (it will
# be used as an upper bound in some calculations).
def uniqueness_indices(v):
    a = np.nonzero(1 - (v[1:] == v[:-1]))[0] +1
    b = np.empty(len(a) + 2, dtype=int)
    b[0] = 0
    b[-1] = len(v)
    b[1:-1] = a
    return b

def get_join_left_indices(a_start_indices, a_len, b_len):
    max_len = a_len.max()
    indexes = np.arange(max_len) + a_start_indices[:, np.newaxis]
    bounds = np.repeat((a_start_indices + a_len)[:, np.newaxis], max_len, axis=1)
    repeated_indexes = np.repeat(indexes, b_len, axis=0).flatten()
    repeated_bounds = np.repeat(bounds, b_len, axis=0).flatten()
    return repeated_indexes[repeated_indexes < repeated_bounds]

def get_join_right_indices(b_start_indices, a_len, b_len):
    max_len = b_len.max()
    indexes = (np.arange(max_len) + b_start_indices[:, np.newaxis]).flatten()
    bounds = np.repeat(b_start_indices + b_len, max_len)
    repeats = np.repeat(a_len, max_len)
    selected = indexes < bounds
    return np.repeat(indexes[selected], repeats[selected])

def get_join_indices(left, right):
    # get first index of each unique value
    a_uniq_indices = uniqueness_indices(left)
    b_uniq_indices = uniqueness_indices(right)
    # get number of occurrences of each unique value
    a_uniq_len = a_uniq_indices[1:] - a_uniq_indices[:-1]
    b_uniq_len = b_uniq_indices[1:] - b_uniq_indices[:-1]
    # get unique values
    a_uniq_vals = left[a_uniq_indices[:-1]]
    b_uniq_vals = right[b_uniq_indices[:-1]]
    # find indices of equal values on left and right
    a_uniq_join_indices, b_uniq_join_indices = merge_indices(a_uniq_vals, b_uniq_vals)
    if a_uniq_join_indices is None:
        return None, None
    # retrieve first index and number of occurrences in previous indexing
    a_start_indices, a_len = a_uniq_indices[a_uniq_join_indices], a_uniq_len[a_uniq_join_indices]
    b_start_indices, b_len = b_uniq_indices[b_uniq_join_indices], b_uniq_len[b_uniq_join_indices]
    # apply cartesian products
    left_indices = get_join_left_indices(a_start_indices, a_len, b_len)
    right_indices = get_join_right_indices(b_start_indices, a_len, b_len)
    # return indices
    return left_indices, right_indices

def merge_join(left_s, right_s, left_col, right_col):
    # sort sources on appropriate column
    left_s = left_s.sort(left_col)
    right_s = right_s.sort(right_col)
    # duplicate join column at position 0
    alt_left_s = left_s.select(left_col, *left_s.columns)
    alt_right_s = right_s.select(right_col, *right_s.columns)
    # build compute function
    def compute():
        # indices of columns except the one duplicated (at position 0)
        # (will be used later)
        left_col_indices = range(1, len(alt_left_s.columns))
        right_col_indices = range(1, len(alt_right_s.columns))
        # iterate over each source
        left_it = fix_spanning_repeated_values(alt_left_s.chunks())
        right_it = fix_spanning_repeated_values(alt_right_s.chunks())
        # forward streams and process chunks in a loop
        try:
            left_chunk = next(left_it)
            right_chunk = next(right_it)
            while True:
                left_col0 = left_chunk.columns[0]
                right_col0 = right_chunk.columns[0]
                # if chunk intervals have an empty intersection, forward
                # one of the iterators.
                # note: since sources are sorted, we know that col0[0]
                # is the minimum value of the chunk and col0[-1] is the
                # maximum value.
                if left_col0[-1] < right_col0[0]:
                    left_chunk = next(left_it)      # forward on the left
                    continue
                if right_col0[-1] < left_col0[0]:
                    right_chunk = next(right_it)    # forward on the right
                    continue
                # compute merge indices
                left_indices, right_indices = get_join_indices(left_col0, right_col0)
                if left_indices is not None:  # note: if not None, then right_indices is not None either
                    left = left_chunk[left_indices, left_col_indices]
                    right = right_chunk[right_indices, right_col_indices]
                    merged = left | right   # paste columns
                    yield merged
                # forward for next loop
                if left_col0[-1] < right_col0[-1]:
                    left_chunk = next(left_it)      # forward on the left
                else:
                    right_chunk = next(right_it)    # forward on the right
        except StopIteration:
            return
    # build source
    source = SourceTypes.ChunksComputedSource('<join>', compute)
    # rebind columns
    for in_source in (left_s, right_s):
        for col in in_source.all_columns:
            source.all_columns.append(col)
        for col in in_source.columns:
            source.columns.append(col)
    return source
