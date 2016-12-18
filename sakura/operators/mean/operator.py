#!/usr/bin/env python
from sakura.daemon.processing.operator import Operator
from sakura.daemon.processing.parameter import NumericColumnSelection

class MeanOperator(Operator):
    NAME = "Mean"
    SHORT_DESC = "Get the mean value of a numeric column."
    def construct(self):
        # inputs
        self.input_table = self.register_input('Input table')
        # outputs
        self.output_table = self.register_output('Mean result')
        self.output_table.add_column('Mean', float)
        self.output_table.length = 1
        # parameters
        self.input_column = self.register_parameter('Input column',
                NumericColumnSelection(self.input_table))
    def compute_output_table(self, output_table, row_start, row_end):
        # * we have only 1 output table, thus output_table = self.output_table
        # * we declared a static length of 1,
        #   thus we assume row_start = 0 & row_end = 1
        res = 0
        num = 0
        idx = self.input_column.index
        for row in self.input_table:
            res += row[idx]
            num += 1
        return ((float(res)/num,),)
