#!/usr/bin/env python
from sakura.daemon.processing.operator import Operator
from sakura.daemon.processing.source import ComputedSource
from numpy.lib import recfunctions

from time import time
import numpy as np

DEBUG = False

class colsselection(Operator):
    NAME = "Columns Selection"
    SHORT_DESC = "Select columns from a table."
    TAGS = ["Filter"]

    def construct(self):
        if DEBUG: print('colsselection -- CONSTRUCT')
        self.selected_columns = []
        # input
        self.input_plug = self.register_input('Input table')
        # output
        self.output_plug = self.register_output('Output table')
        # additional tabs
        self.register_tab('Selection', 'colsselection.html')

    def handle_event(self, ev_type, time_credit, **info):
        if DEBUG: print('colsselection -- EVENT', ev_type)

        if not self.input_plug.connected():
            return { 'issue': 'NO DATA: Input is not connected.' }

        if ev_type == 'get_data':
            source = self.input_plug.source
            headers = []
            for c in self.input_plug.columns:
                headers.append(c._label)
            if DEBUG: print('colsselection -- HEADERS', headers)
            it = next(source.chunks())
            return {'headers': headers,
                    'rows': it[:20],
                    'selected': self.selected_columns,
                    'more': len(it) > 20}

        elif ev_type == 'set_cols':
            self.selected_columns = info['cols']
            if len(self.selected_columns):
                source = self.input_plug.source
                self.output_plug.source = source.select_columns(*self.selected_columns)
            else:
                self.output_plug.source = None
            return {}
        else:
            print('unknown event', ev_type)

        return {}
