#!/usr/bin/env python
from sakura.daemon.processing.stream import ComputedStream
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
STREAM = ComputedStream('People', compute)
STREAM.add_column("Name", str)
STREAM.add_column("Age", int)
STREAM.add_column("Gender", (str, 8))
STREAM.add_column("Height", int)
STREAM.length = len(PEOPLE)
