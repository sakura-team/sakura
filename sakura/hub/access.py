from itertools import count
from enum import Enum

ACCESS_SCOPES = Enum('ACCESS_SCOPES', zip('public restricted private'.split(), count()))
