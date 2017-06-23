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
        print('In contruct')
        # inputs
        self.input_stream = self.register_input('GPS data')
        # parameters
        self.lng_column_param = self.register_parameter('input longitude',
                TagBasedColumnSelection(self.input_stream, 'longitude'))
        self.lat_column_param = self.register_parameter('input latitude',
                TagBasedColumnSelection(self.input_stream, 'latitude'))
        # additional tabs
        self.register_tab('Map', 'map.html')

    def handle_event(self, event):
        ev_type = event[0]
        if ev_type == 'map_clicked':
            #latlng = event[1]
            pass
        elif ev_type == 'map_move':
            info = event[1]
            # get columns selected in combo parameters
            lng_column, lat_column = \
                self.lng_column_param.value, self.lat_column_param.value
            # filter input stream as much as possible:
            # - select useful columns only
            # - restrict to visible area
            stream = self.input_stream
            stream = stream.select_columns(lng_column, lat_column)
            stream = stream.filter(lng_column >= info['westlng'])
            stream = stream.filter(lng_column <= info['eastlng'])
            stream = stream.filter(lat_column >= info['southlat'])
            stream = stream.filter(lat_column <= info['northlat'])
            # compute heatmap
            return { 'heatmap': heatmap.generate(lnglat=stream, **info) }
        elif ev_type == 'new_zone':
            lng_column, lat_column = \
                self.lng_column_param.value, self.lat_column_param.value
            stream = self.input_stream
            stream = stream.select_columns(lng_column,lat_column)
            for chunk in stream.chunks():
                 lng, lat = chunk.columns
            return { 'tweetsmap': dict(lat = lat.tolist(), lng = lng.tolist()) }
            
