#!/usr/bin/env python
from sakura.daemon.processing.source import ComputedSource
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
SOURCE = ComputedSource('People', compute)
SOURCE.add_column("Name", str)
SOURCE.add_column("Age", int)
SOURCE.add_column("Gender", (str, 8))
SOURCE.add_column("Height", int)
SOURCE.length = len(PEOPLE)
