#!/usr/bin/env python
import numpy as np
from sakura.daemon.processing.source import ComputedSource, ComputeMode

CHUNK_SIZE = 87     # just to check proper chunk realignment
COL_TYPE = ('Multiples of 5', np.uint)
NUM_CHUNKS = 20
LEN = NUM_CHUNKS * CHUNK_SIZE

def compute():
    chunk = np.arange(CHUNK_SIZE, dtype=np.uint) * 5
    for _ in range(NUM_CHUNKS):
        yield chunk.astype([COL_TYPE])
        chunk += 5 * CHUNK_SIZE

# dataset description
SOURCE = ComputedSource(
            'Multiples of 5',
            compute,
            compute_mode = ComputeMode.CHUNKS)
SOURCE.add_column(*COL_TYPE)
SOURCE.length = LEN
