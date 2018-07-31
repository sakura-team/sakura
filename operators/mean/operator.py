#!/usr/bin/env python
from sakura.daemon.processing.operator import Operator
from sakura.daemon.processing.parameter import NumericColumnSelection
from sakura.daemon.processing.source import ComputedSource

class MeanOperator(Operator):
    NAME = "Mean"
    SHORT_DESC = "Get the mean value of a numeric column."
    TAGS = [ "statistics", "aggregate" ]
    def construct(self):
        # inputs
        self.input = self.register_input('Mean input data')
        
        # outputs
        output_source = ComputedSource('Mean result', self.compute)
        output_source.add_column('Mean', float)
        output_source.length = 1
        self.register_output('Mean result', output_source)
        
        # parameters
        self.input_column_param = self.register_parameter(
                NumericColumnSelection('Input column', self.input))
                
    def compute(self):
        column_idx = self.input_column_param.col_index
        column = self.input.columns[column_idx]
        res = 0
        num = 0
        for chunk in column.chunks():
            res += chunk.sum()
            num += chunk.size
        mean = float(res)/num
        # our output has only 1 row and 1 column
        yield (mean,)
