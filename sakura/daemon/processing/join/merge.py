import numpy as np
from sakura.daemon.processing.sources.types import SourceTypes

# This merge join algorithm works when joining strictly increasing
# columns (thus values must be unique).

def merge_join_right_indices(left, right):
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

def merge_join_left_indices(left, right):
    return merge_join_right_indices(right, left)

# reduce vector v to values in the given interval
# return offset and section of v
def reduce_min_max(v, min_val, max_val):
    v_idx_min, v_idx_max = np.searchsorted(v, (min_val, max_val))
    if v_idx_max < len(v) and v[v_idx_max] == max_val:
        v_idx_max += 1
    return v_idx_min, v[v_idx_min:v_idx_max]

def merge_join_indices(left, right):
    # first, reduce chunks to intersection of their min-max interval
    right_offset, right = reduce_min_max(right, left[0], left[-1])
    if len(right) == 0:
        return None, None
    left_offset, left = reduce_min_max(left, right[0], right[-1])
    if len(left) == 0:
        return None, None
    # check which way will be more efficient
    if len(left) > len(right):
        right_indices = merge_join_right_indices(left, right)
        if len(right_indices) == 0:
            return None, None
        right = right[right_indices]
        offset, left = reduce_min_max(left, right[0], right[-1])
        left_offset += offset
        if len(left) == 0:
            return None, None
        left_indices = merge_join_left_indices(left, right)
    else:
        left_indices = merge_join_left_indices(left, right)
        if len(left_indices) == 0:
            return None, None
        left = left[left_indices]
        offset, right = reduce_min_max(right, left[0], left[-1])
        right_offset += offset
        if len(right) == 0:
            return None, None
        right_indices = merge_join_right_indices(left, right)
    # return
    return left_indices + left_offset, right_indices + right_offset

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
        left_it = alt_left_s.chunks()
        right_it = alt_right_s.chunks()
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
                left_indices, right_indices = merge_join_indices(left_col0, right_col0)
                if left_indices is not None:  # note: if not None, then right_indices is not None either
                    left = left_chunk[left_indices].__select_columns_indexes__(left_col_indices)
                    right = right_chunk[right_indices].__select_columns_indexes__(right_col_indices)
                    merged = left.__paste_right__(right)
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
