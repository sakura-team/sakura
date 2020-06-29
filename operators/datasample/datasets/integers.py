#!/usr/bin/env python
import numpy as np
from sakura.daemon.processing.source import ComputedSource, ComputeMode

CHUNK_SIZE = int(1E+5)
LEN = int(1E+7)
NUM_CHUNKS = int(LEN / CHUNK_SIZE)
COL_TYPE = ('Integers', np.uint16)

def compute():
    for i in range(NUM_CHUNKS):
        chunk = np.random.randint(NUM_CHUNKS, 1000, CHUNK_SIZE, np.uint16)
        i += 1
        chunk[-i:] = i
        yield chunk.astype([COL_TYPE])

# dataset description
SOURCE = ComputedSource(
            'Almost random integers',
            compute,
            compute_mode = ComputeMode.CHUNKS)
SOURCE.add_column(*COL_TYPE)
SOURCE.length = LEN
