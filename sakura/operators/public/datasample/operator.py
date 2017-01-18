#!/usr/bin/env python
import random
from sakura.daemon.processing.operator import Operator

# info about output1
OUTPUT1_COLUMNS = (
    ("Name", str), ("Age", int),  ("Gender", str), ("Height", int))
OUTPUT1 = (
    ("John", 52, "male", 175),
    ("Alice", 34, "female", 184),
    ("Bob", 31, "male", 156),
    ("Jane", 38, "female", 164)
)

# info about output2
OUTPUT2_LENGTH = 1000

class DataSampleOperator(Operator):
    NAME = "Data Sample"
    SHORT_DESC = "Data Sample."
    TAGS = [ "testing", "datasource" ]
    def construct(self):
        # no inputs
        pass
        # outputs:
        # - output1: dump of OUTPUT1 (see above)
        # - output2: generate OUTPUT2_LENGTH random integers
        output1 = self.register_output('People', self.compute1)
        output1.length = len(OUTPUT1)
        for colname, coltype in OUTPUT1_COLUMNS:
            output1.add_column(colname, coltype)
        output2 = self.register_output('Random integers', self.compute2)
        output2.add_column('Integers', int)
        # no parameters
        pass
    def compute1(self):
        for row in OUTPUT1:
            yield row
    def compute2(self):
        for row_idx in range(OUTPUT2_LENGTH):
            yield (random.randint(0, 1000),)
