#!/usr/bin/env python
from sakura.daemon.processing.operator import Operator
from sakura.daemon.processing.source import ComputedSource
from numpy.lib import recfunctions

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
                'NUMERIC_COLUMN_SELECTION', 'X (abscissa)', self.input)
        self.input_column_param_y = self.register_parameter(
                'NUMERIC_COLUMN_SELECTION', 'Y (ordinate)', self.input)

        # additional tabs
        self.register_tab('Plot', 'plot.html')

        self.iterator = None

    def handle_event(self, ev_type, time_credit):
        print(time())
        deadline = time() + time_credit

        if not self.input.connected():
            return { 'issue': 'NO DATA: Input is not connected.' }

        if ev_type == 'get_data': #first time data is asked
            column_x        = self.input_column_param_x.column
            column_y        = self.input_column_param_y.column
            source          = self.input.source
            source          = source.select(column_x, column_y)
            self.iterator   = source.chunks()

        big_chunk = None
        for chunk in self.iterator:
            if big_chunk is None:
                big_chunk = chunk
            else:
                # concatenate
                big_chunk = recfunctions.stack_arrays((big_chunk, chunk))
            if time() > deadline:
                return {'dp': big_chunk, 'done': False}
        return {'dp': big_chunk, 'done': True}
