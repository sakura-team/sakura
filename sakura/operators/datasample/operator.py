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
    def construct(self):
        # no inputs
        pass
        # outputs
        self.output_table = self.register_output('Data')
        self.output_table.length = len(DATA)
        for colname, coltype in DATA_COLUMNS:
            self.output_table.add_column(colname, coltype)
        # no parameters
        pass
    def compute_output_table(self, output_table, row_start, row_end):
        # * we have only 1 output table, thus output_table = self.output_table
        row_end = min(row_end, len(DATA))
        for row_idx in range(row_start, row_end):
            yield DATA[row_idx]
