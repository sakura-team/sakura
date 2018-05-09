#!/usr/bin/env python
import numpy as np
from sakura.daemon.processing.stream import ComputedStream, ComputeMode

CHUNK_SIZE = int(1E+5)
LEN = int(1E+7)
NUM_CHUNKS = int(LEN / CHUNK_SIZE)
COL_TYPE = ('Integers', np.uint16)

def compute():
    for _ in range(NUM_CHUNKS):
        chunk = np.random.randint(0, 1000, CHUNK_SIZE, np.uint16)
        yield chunk.astype([COL_TYPE])

# dataset description
STREAM = ComputedStream(
            'Random integers',
            compute,
            compute_mode = ComputeMode.CHUNKS)
STREAM.add_column(*COL_TYPE)
STREAM.length = LEN
