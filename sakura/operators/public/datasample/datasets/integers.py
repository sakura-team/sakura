#!/usr/bin/env python
import random

DATA_LEN = 1000
DATA = tuple((random.randint(0, 1000),) for i in range(DATA_LEN))

def compute():
    for row in DATA:
        yield row

# dataset description
NAME = 'Random integers'
COLUMNS = (('Integers', int),)
COMPUTE_CALLBACK = compute
LENGTH = DATA_LEN
