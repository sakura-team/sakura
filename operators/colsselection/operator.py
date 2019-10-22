#!/usr/bin/env python
from sakura.daemon.processing.operator import Operator
from sakura.daemon.processing.source import ComputedSource
from numpy.lib import recfunctions

from time import time
import numpy as np

class colsselection(Operator):
    NAME = "Columns Selection"
    SHORT_DESC = "Select columns from a table."
    TAGS = ["Filter"]

    def construct(self):

        self.selected_columns = []

        # input
        self.input_plug = self.register_input('Input table')

        # output
        self.output_plug = self.register_output('Output table')
        #output_source = ComputedSource('Output table', self.compute)

        # additional tabs
        self.register_tab('Selection', 'colsselection.html')

    def handle_event(self, ev_type, time_credit, **info):
        if ev_type == 'get_data':
            source = self.input_plug.source
            headers = []
            for c in self.input_plug.columns:
                headers.append(c._label)

            it = next(source.chunks())
            return {'headers': headers, 'rows': it}

        elif ev_type == 'set_cols':
            self.selected_columns = info['cols']
        else:
            print('unknown event', ev_type)

    def compute(self):
        pass
