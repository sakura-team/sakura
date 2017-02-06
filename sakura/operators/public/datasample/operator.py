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
tmp = []
for row in range(OUTPUT2_LENGTH):
    tmp.append((random.randint(0, 1000),))
OUTPUT2 = tuple(tmp)

# info about output3 (length is not fixed)
OUTPUT3_LENGTH = random.randint(100, 200)
            
class DataSampleOperator(Operator):
    NAME = "Data Sample"
    SHORT_DESC = "Data Sample."
    TAGS = [ "testing", "datasource" ]
    def construct(self):
        # no inputs
        pass
        # outputs:
        # - output1: dump of OUTPUT1 (see above)
        # - output2: dump of OUTPUT2 (randomly generated integers)
        # - output3: generate OUTPUT2_LENGTH random integers
        output1 = self.register_output('People', self.compute1)
        output1.length = len(OUTPUT1)
        for colname, coltype in OUTPUT1_COLUMNS:
            output1.add_column(colname, coltype)
        
        output2 = self.register_output('1000 integers', self.compute2)
        output2.length = OUTPUT2_LENGTH
        output2.add_column('Integers', int)
        
        output3 = self.register_output('Random integers', self.compute3)
        output3.add_column('Integers', int)
       
        # no parameters
        pass
    def compute1(self):
        for row in OUTPUT1:
            yield row
    def compute2(self):
        for row in OUTPUT2:
            yield row
    def compute3(self):
        for row_idx in range(OUTPUT3_LENGTH):
            yield (random.randint(0, 1000),)

