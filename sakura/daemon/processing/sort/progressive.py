import numpy as np
from sakura.daemon.processing.sort.tools import get_cut_position
from sakura.common.chunk import NumpyChunk
from sakura.common.tools import Timer
from sakura.common.exactness import EXACT, APPROXIMATE

MIN_OUTPUT_CHUNK_SIZE = 100
# progressive sort algorithm, able to output approximate chunks
# once in a while in case of long calculations.
# it works by partitionning sort_buf to accumulate lowest values
# on its left part.
def progressive_sorted_chunks(orig_source, sort_columns):
    work_columns = list(sort_columns) + list(orig_source.columns)
    work_source = orig_source.select(*work_columns)
    sort_col_indexes = np.arange(len(sort_columns))
    other_col_indexes = np.arange(len(orig_source.columns)) + sort_col_indexes.size
    timer = Timer(period=0.2)
    offset = 0
    output_chunk_size = None
    # size of sort_buf must be twice the output_chunk_size.
    # we delay its initialization up to the receival of the first chunk.
    sort_buf = None
    sort_cols_lower_bound = None
    while True:
        source = work_source
        if sort_cols_lower_bound is not None:
            # caution: we are looking for rows with sort_columns *strictly* higher
            # than sort_cols_lower_bound, but in case of several sort columns
            # we may have some of them lower than (or equal to) the corresponding
            # lower bound, e.g. (5, 6, 4) > (5, 5, 12).
            # we cannot express this with sakura, so let's check only for the first
            # column and we will recheck the global strict ordering below.
            source = source.where(sort_columns[0] >= sort_cols_lower_bound[0])
        curr_chunk = None
        eq_values_detected = False
        for chunk in source.chunks():
            # upon reception of first chunk, select an appropriate output_chunk_size
            # (considering the size of this first chunk) and initialize sort_buf.
            if sort_buf is None:
                if chunk.size >= MIN_OUTPUT_CHUNK_SIZE:
                    output_chunk_size = chunk.size
                else:
                    output_chunk_size = MIN_OUTPUT_CHUNK_SIZE
                sort_buf = np.empty(2*output_chunk_size, work_source.get_dtype()).view(NumpyChunk)
            if sort_cols_lower_bound is not None:
                # check strict ordering
                chunk = chunk[chunk[:,sort_col_indexes] > sort_cols_lower_bound]
                if chunk.size == 0:
                    continue
            if curr_chunk is None:
                sort_buf[:chunk.size] = chunk
                curr_chunk = sort_buf[:chunk.size]
            else:
                sort_buf[curr_chunk.size:curr_chunk.size+len(chunk)] = chunk
                sort_buf_level = curr_chunk.size + chunk.size
                if sort_buf_level <= output_chunk_size:
                    curr_chunk = sort_buf[:sort_buf_level]
                else:
                    sort_buf[:sort_buf_level].data.partition(output_chunk_size)
                    curr_chunk = sort_buf[:output_chunk_size]
            # in case of long calculations, report an approximate
            # chunk once in a while
            if timer.late():
                curr_chunk.sort()
                curr_chunk.exactness = APPROXIMATE
                yield curr_chunk[:,other_col_indexes]
                timer.reset()
        if curr_chunk is None:
            return
        curr_chunk.sort()
        # detect series of equal values
        if curr_chunk[0,sort_col_indexes] == curr_chunk[-1,sort_col_indexes]:
            # we have many times the same value for sort columns,
            # output all rows with these values and then continue
            vals = tuple(curr_chunk[:,sort_col_indexes].data[0])
            source = orig_source
            for col, val in zip(sort_columns, vals):
                source = source.where(col == val)
            yield from source.chunks(output_chunk_size)
            sort_cols_lower_bound = vals
        else:
            cut_pos = get_cut_position(curr_chunk[:,sort_col_indexes])
            curr_chunk.exactness = EXACT
            yield curr_chunk[:cut_pos,other_col_indexes]
            timer.reset()
            sort_cols_lower_bound = tuple(curr_chunk[:,sort_col_indexes].data[cut_pos-1])
