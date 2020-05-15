#!/usr/bin/env python
import numpy as np
from sakura.daemon.processing.source import ComputedSource, ComputeMode

CHUNK_SIZE = 50
COL_TYPE = ('Multiples of 3', np.uint)
NUM_CHUNKS = 20
LEN = NUM_CHUNKS * CHUNK_SIZE

def compute():
    chunk = np.arange(CHUNK_SIZE, dtype=np.uint) * 3
    for _ in range(NUM_CHUNKS):
        yield chunk.astype([COL_TYPE])
        chunk += 3 * CHUNK_SIZE

# dataset description
SOURCE = ComputedSource(
            'Multiples of 3',
            compute,
            compute_mode = ComputeMode.CHUNKS)
SOURCE.add_column(*COL_TYPE)
SOURCE.length = LEN
