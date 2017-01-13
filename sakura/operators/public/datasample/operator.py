#!/usr/bin/env python
import random
from sakura.daemon.processing.operator import Operator

DATA1_COLUMNS = (
    ("Name", str), ("Age", int),  ("Gender", str), ("Height", int))
DATA1 = (
    ("John", 52, "male", 175),
    ("Alice", 34, "female", 184),
    ("Bob", 31, "male", 156),
    ("Jane", 38, "female", 164)
)
DATA2_LENGTH = 1000

class DataSampleOperator(Operator):
    NAME = "Data Sample"
    SHORT_DESC = "Data Sample."
    TAGS = [ "testing", "datasource" ]
    def construct(self):
        # no inputs
        pass
        # outputs
        self.output_table1 = self.register_output('Data1', self.compute_table1)
        self.output_table1.length = len(DATA1)
        for colname, coltype in DATA1_COLUMNS:
            self.output_table1.add_column(colname, coltype)
        self.output_table2 = self.register_output('Data2', self.compute_table2)
        self.output_table2.add_column('Integers', int)
        # no parameters
        pass
    def compute_table1(self):
        for row_idx in range(len(DATA1)):
            yield DATA1[row_idx]
    def compute_table2(self):
        for row_idx in range(DATA2_LENGTH):
            yield (random.randint(0, 1000),)
