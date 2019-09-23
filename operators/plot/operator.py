#!/usr/bin/env python
from sakura.daemon.processing.operator import Operator
from sakura.daemon.processing.parameter import NumericColumnSelection
from sakura.daemon.processing.source import ComputedSource

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

        self.iterator = None

    def handle_event(self, ev_type, time_credit):
        print(time())
        deadline = time() + time_credit

        if not self.input.connected():
            return { 'issue': 'NO DATA: Input is not connected.' }

        if ev_type == 'get_data': #first time data is asked
            column_x        = self.input_column_param_x.col_index
            column_y        = self.input_column_param_y.col_index
            source          = self.input.source
            source          = source.select_columns(column_x, column_y)
            self.iterator   = source.chunks()

        dp = []
        for chunk in self.iterator:
            for x, y in chunk:
                dp.append({'x': x, 'y': y})
                if time() > deadline:
                    return {'dp': dp, 'done': False}
        return {'dp': dp, 'done': True}
