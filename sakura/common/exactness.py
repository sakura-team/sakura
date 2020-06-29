from enum import IntEnum

class Exactness(IntEnum):
    UNDEFINED = 0
    APPROXIMATE = 1
    EXACT = 2

# shortcuts
EXACT = Exactness.EXACT
APPROXIMATE = Exactness.APPROXIMATE
UNDEFINED = Exactness.UNDEFINED
