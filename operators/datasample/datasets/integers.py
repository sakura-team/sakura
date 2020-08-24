#!/usr/bin/env python
import numpy as np
from sakura.daemon.processing.source import ComputedSource, ComputeMode

CHUNK_SIZE = int(1E+3)
LEN = int(1E+5)
NUM_CHUNKS = int(LEN / CHUNK_SIZE)
COL_TYPE = ('Integers', np.uint16)
DATA = None

def compute():
    global DATA
    if DATA is None:
        DATA = np.empty(LEN, dtype=np.uint16)
        level = 0
        i = 1
        while level < LEN:
            DATA[level:level+i] = i
            level = level+i
            i += 1
        np.random.shuffle(DATA)
    print('COMPUTE!!!!!!!!!!!!!!!!!!!!!!!!!!')
    for i in range(NUM_CHUNKS):
        yield DATA[i*CHUNK_SIZE:(i+1)*CHUNK_SIZE].astype([COL_TYPE])

# dataset description
SOURCE = ComputedSource(
            'Random integers',
            compute,
            compute_mode = ComputeMode.CHUNKS)
SOURCE.add_column(*COL_TYPE)
SOURCE.length = LEN
