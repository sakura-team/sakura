#!/usr/bin/env python
import random
from sakura.daemon.processing.stream import SimpleStream

DATA_LEN = 1000
DATA = tuple((random.randint(0, 1000),) for i in range(DATA_LEN))

def compute():
    for row in DATA:
        yield row

# dataset description
STREAM = SimpleStream('Random integers', compute)
STREAM.add_column('Integers', int)
STREAM.length = DATA_LEN
