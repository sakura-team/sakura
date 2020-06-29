# when sorting chunks, the last value(s) of a chunk may equal
# the first value(s) of the next one.
# in some cases, we need to temporarily discard these last values
# of a chunk and let them be processed at next iteration.
def get_cut_position(chunk):
    if len(chunk) < 2:
        return 0
    if chunk[-2] != chunk[-1]:  # fast path
        return chunk.size -1
    if chunk[0] == chunk[-1]:  # fast path
        return 0
    return chunk.searchsorted(chunk[-1])
