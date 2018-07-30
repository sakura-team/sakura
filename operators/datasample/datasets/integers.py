#!/usr/bin/env python
import numpy as np
from sakura.daemon.processing.source import ComputedSource, ComputeMode

CHUNK_SIZE = int(1E+5)
LEN = int(1E+7)
NUM_CHUNKS = int(LEN / CHUNK_SIZE)
COL_TYPE = ('Integers', np.uint16)

def compute():
    for _ in range(NUM_CHUNKS):
        chunk = np.random.randint(0, 1000, CHUNK_SIZE, np.uint16)
        yield chunk.astype([COL_TYPE])

# dataset description
SOURCE = ComputedSource(
            'Random integers',
            compute,
            compute_mode = ComputeMode.CHUNKS)
SOURCE.add_column(*COL_TYPE)
SOURCE.length = LEN
