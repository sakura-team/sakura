#!/usr/bin/env python
from sakura.daemon.processing.operator import Operator
from sakura.daemon.processing.parameter import NumericColumnSelection
from sakura.daemon.processing.stream import ComputedStream

import numpy as np

class PlotOperator(Operator):
    NAME = "Plot"
    SHORT_DESC = "Displays a plot from a list of 2D points"
    TAGS = [ "visualisation"]
    def construct(self):
        # inputs
        self.input = self.register_input('Table with X and Y column')

        # parameters
        self.input_column_param_x = self.register_parameter('X (abscissa)',
                NumericColumnSelection(self.input))
        self.input_column_param_y = self.register_parameter('Y (ordinate)',
                NumericColumnSelection(self.input))

        # additional tabs
        self.register_tab('Plot', 'plot.html')

    def handle_event(self, event):
        if not self.input.connected():
            return { 'issue': 'NO DATA: Input is not connected.' }

        if event[0] == 'get_data':
            dp = []
            column_x = self.input.columns[self.input_column_param_x.value]
            column_y = self.input.columns[self.input_column_param_y.value]
            for chunk_x, chunk_y in zip(column_x.chunks(), column_y.chunks()):
                for x, y in zip(chunk_x, chunk_y):
                    dp.append({'x': x, 'y': y})
            return {'dp': dp}

        return {'issue': 'Unknown event'}
