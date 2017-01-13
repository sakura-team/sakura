#!/usr/bin/env python
from sakura.daemon.processing.operator import Operator
from sakura.daemon.processing.parameter import NumericColumnSelection

class MeanOperator(Operator):
    NAME = "Mean"
    SHORT_DESC = "Get the mean value of a numeric column."
    TAGS = [ "statistics", "aggregate" ]
    def construct(self):
        # inputs
        self.input_table = self.register_input('Input table')
        # outputs
        self.output_table = self.register_output('Mean result', self.compute)
        self.output_table.add_column('Mean', float)
        self.output_table.length = 1
        # parameters
        self.input_column = self.register_parameter('Input column',
                NumericColumnSelection(self.input_table))
    def compute(self):
        res = 0
        num = 0
        idx = self.input_column.index
        for row in self.input_table:
            res += row[idx]
            num += 1
        return ((float(res)/num,),)
