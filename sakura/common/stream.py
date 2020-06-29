import numpy as np
from sakura.common.chunk import NumpyChunk
from sakura.common.exactness import EXACT, APPROXIMATE, UNDEFINED, Exactness

def reassemble_chunk_stream(it, dt, chunk_size):
    if chunk_size is None:
        return it   # nothing to do
    def reassembled(it):
        buf_chunk = NumpyChunk.empty(chunk_size, dt, UNDEFINED)
        buf_level = 0
        for chunk in it:
            if chunk.exact():
                # depending on requested chunk_size, we may have to cut this
                # chunk into several parts.
                while chunk.size > 0:
                    chunk_part = chunk[:chunk_size-buf_level]
                    buf_chunk[buf_level:buf_level+chunk_part.size] = chunk_part
                    buf_level += chunk_part.size
                    if buf_level == chunk_size:
                        buf_chunk.exactness = EXACT
                        yield buf_chunk
                        buf_level = 0
                    chunk = chunk[chunk_part.size:]
            else:
                # size of approximate chunks is lower or equal to chunk_size.
                # we concatenate current exact rows of buf_chunk with approximate
                # ones of this chunk.
                chunk_part = chunk[:chunk_size-buf_level]
                buf_chunk[buf_level:buf_level+chunk_part.size] = chunk_part
                inexact_chunk = buf_chunk[:buf_level+chunk_part.size]
                inexact_chunk.exactness = APPROXIMATE
                yield inexact_chunk
        if buf_level > 0:
            # last exact chunk is the only one which may have a size lower than
            # chunk_size
            buf_chunk = buf_chunk[:buf_level]
            buf_chunk.exactness = EXACT
            yield buf_chunk
    return reassembled(it)

def normalize_chunk_stream(it):
    for chunk in it:
        chunk = chunk.view(NumpyChunk)
        # if not specified we consider the chunk is exact
        if chunk.exactness == UNDEFINED:
            chunk.exactness = EXACT
        yield chunk

def normalize_value_stream(it):
    for val in it:
        # if not specified we consider the value is exact
        if isinstance(val, tuple) and len(val) == 2 and isinstance(val[1], Exactness):
            yield val   # val is already a tuple (<row>, <exactness>)
        else:
            yield val, EXACT
