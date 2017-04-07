#!/usr/bin/env python
PEOPLE_COLUMNS = (
    ("Name", str), ("Age", int),  ("Gender", str), ("Height", int))
PEOPLE = (
    ("John", 52, "male", 175),
    ("Alice", 34, "female", 184),
    ("Bob", 31, "male", 156),
    ("Jane", 38, "female", 164)
)

def compute():
    for row in PEOPLE:
        yield row

# dataset description
NAME = 'People'
COLUMNS = PEOPLE_COLUMNS
LENGTH = len(PEOPLE)
COMPUTE_CALLBACK = compute
