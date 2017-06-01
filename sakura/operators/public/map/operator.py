#!/usr/bin/env python
import itertools, numpy as np
from sakura.daemon.processing.operator import Operator
from sakura.daemon.processing.parameter import TagBasedColumnSelection
from . import heatmap
from time import time

class MapOperator(Operator):
    NAME = "Map"
    SHORT_DESC = "Map display and selection operator."
    TAGS = [ "geo", "map", "selection" ]
    def construct(self):
        # inputs
        self.input_markers = self.register_input('Markers')
        # parameters
        self.lng_column_param = self.register_parameter('input longitude',
                TagBasedColumnSelection(self.input_markers, 'longitude'))
        self.lat_column_param = self.register_parameter('input latitude',
                TagBasedColumnSelection(self.input_markers, 'latitude'))
        # additional tabs
        self.register_tab('Map', 'map.html')

    def handle_event(self, event):
        ev_type = event[0]
        if ev_type == 'map_clicked':
            #latlng = event[1]
            pass
        elif ev_type == 'map_move':
            info = event[1]
            lng_column, lat_column = \
                self.lng_column_param.value, self.lat_column_param.value
            info['lnglat'] = self.input_markers.select_columns(
                lng_column,
                lat_column
            )
            return { 'heatmap': heatmap.generate(**info) }
