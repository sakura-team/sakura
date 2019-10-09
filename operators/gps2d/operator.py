#!/usr/bin/env python
from sakura.daemon.processing.operator import Operator
from sakura.daemon.processing.parameter import NumericColumnSelection
from sakura.daemon.processing.parameter import StrColumnSelection
from sakura.daemon.processing.source import ComputedSource
from numpy.lib import recfunctions

from time import time
import numpy as np

class gps2d(Operator):
    NAME = "GPS_2D"
    SHORT_DESC = "Displays trajectories on a 2D map."
    TAGS = [ "visualisation"]

    def construct(self):
        # inputs
        self.input = self.register_input('Input gps table')

        # parameters
        self.input_column_param_id = self.register_parameter(
                StrColumnSelection('Trajectory ids', self.input))
        self.input_column_param_lon = self.register_parameter(
                NumericColumnSelection('longitude', self.input))
        self.input_column_param_lon = self.register_parameter(
                NumericColumnSelection('latitude', self.input))

        # additional tabs
        self.register_tab('GPS_2D', 'gps2d.html')

        self.iterator = None

    def handle_event(self, ev_type):
        print(ev_type)
        if not self.input.connected():
            return { 'issue': 'NO DATA: Input is not connected.' }

        if 'get_data' in ev_type:
            if ev_type == 'get_data_first':
                #Init iterator
                column_id       = self.input_column_param_id.col_index
                column_x        = self.input_column_param_lon.col_index
                column_y        = self.input_column_param_lat.col_index
                source          = self.input.source
                source          = source.select_columns(column_id, column_x, column_y)
                self.iterator   = source.chunks()

            chunk = None
            try:
                print('here')
                chunk = self.iterator.next()
                print('there')

                return {'db': chunk, 'end': False}
            except:
                print('issue')
                return {'db': null, 'end': True}
        return {}
