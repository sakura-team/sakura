#!/usr/bin/env python
from sakura.daemon.processing.operator import Operator
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
                'STRING_COLUMN_SELECTION', 'Trajectory ids', self.input)
        self.input_column_param_lon = self.register_parameter(
                'NUMERIC_COLUMN_SELECTION', 'longitude', self.input)
        self.input_column_param_lat = self.register_parameter(
                'NUMERIC_COLUMN_SELECTION', 'latitude', self.input)

        # additional tabs
        self.register_tab('GPS_2D', 'gps2d.html')

        self.iterator = None

    def handle_event(self, ev_type):
        if not self.input.connected():
            return { 'issue': 'NO DATA: Input is not connected.' }

        if 'get_data' in ev_type:
            if ev_type == 'get_data_first':
                #Init iterator
                column_id       = self.input_column_param_id.column
                column_x        = self.input_column_param_lon.column
                column_y        = self.input_column_param_lat.column
                source          = self.input.source
                source          = source.select(column_id, column_x, column_y)
                self.iterator   = source.chunks()

            try:
                chunk = next(self.iterator)
                return {'db': chunk,
                        'max': np.max([(c[2], c[1]) for c in chunk], axis=0),
                        'min': np.min([(c[2], c[1]) for c in chunk], axis=0),
                        'end': False}
            except StopIteration:
                return {'db': None, 'max':None, 'min':None, 'end': True}
        return {'db': None, 'max':None, 'min':None, 'end': True}
