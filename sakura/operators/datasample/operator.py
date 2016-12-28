#!/usr/bin/env python
from sakura.daemon.processing.operator import Operator

DATA_COLUMNS = (
    ("Name", str), ("Age", int),  ("Gender", str))
DATA = (
    ("John", 52, "male"),
    ("Alice", 34, "female"),
    ("Bob", 31, "male"),
    ("Jane", 38, "female")
)

class DataSampleOperator(Operator):
    NAME = "Data Sample"
    SHORT_DESC = "Data Sample."
    TAGS = [ "testing", "datasource" ]
    def construct(self):
        # no inputs
        pass
        # outputs
        self.output_table = self.register_output('Data', self.compute)
        self.output_table.length = len(DATA)
        for colname, coltype in DATA_COLUMNS:
            self.output_table.add_column(colname, coltype)
        # no parameters
        pass
    def compute(self):
        for row_idx in range(len(DATA)):
            yield DATA[row_idx]
