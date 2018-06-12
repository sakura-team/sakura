#!/usr/bin/env python
from sakura.daemon.processing.operator import Operator
from sakura.daemon.processing.parameter import NumericColumnSelection
from sakura.daemon.processing.stream import ComputedStream

from time import time
import numpy as np

class PlotOperator(Operator):
    NAME = "Plot"
    SHORT_DESC = "Displays a plot from a list of 2D points"
    TAGS = [ "visualisation"]
    def construct(self):
        # inputs
        self.input = self.register_input('Table with X and Y column')

        # parameters
        self.input_column_param_x = self.register_parameter(
                NumericColumnSelection('X (abscissa)', self.input))
        self.input_column_param_y = self.register_parameter(
                NumericColumnSelection('Y (ordinate)', self.input))

        # additional tabs
        self.register_tab('Plot', 'plot.html')

    def handle_event(self, event):
        if not self.input.connected():
            return { 'issue': 'NO DATA: Input is not connected.' }

        if event[0] == 'get_data':
            dp = []
            column_x = self.input_column_param_x.col_index
            column_y = self.input_column_param_y.col_index
            #time_credit = 0.3
            #deadline = time() + time_credit
            stream = self.input.select_columns(column_x, column_y)
            for chunk in stream.chunks():
                for x, y in chunk:
                    dp.append({'x': x, 'y': y})
                #if time() > deadline:
                #    break

            return {'dp': dp}

        return {'issue': 'Unknown event'}
