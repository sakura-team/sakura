#!/usr/bin/env python
import itertools, numpy as np, operator
from sakura.daemon.processing.operator import Operator
from sakura.daemon.processing.parameter import TagBasedColumnSelection
from .heatmap import HeatMap
from time import time

class MapOperator(Operator):
    NAME = "Map"
    SHORT_DESC = "Map display and selection operator."
    TAGS = [ "geo", "map", "selection" ]
    def construct(self):
        # inputs
        self.input_stream = self.register_input('GPS data')
        # parameters
        self.lng_column_param = self.register_parameter(
                TagBasedColumnSelection('input longitude', self.input_stream, 'longitude'))
        self.lat_column_param = self.register_parameter(
                TagBasedColumnSelection('input latitude', self.input_stream, 'latitude'))
        # additional tabs
        self.register_tab('Map', 'map.html')
        # custom attributes
        self.curr_heatmap = None
        # we do not know which filtering should be applied yet,
        # so just mirror the input for now.
        self.current_filtered_stream = self.input_stream

    @property
    def output_streams(self):
        return [ self.current_filtered_stream ]

    def filtered_stream(self, westlng, eastlng, southlat, northlat, **args):
        # get columns selected in combo parameters
        lng_col_idx, lat_col_idx = \
            self.lng_column_param.col_index, self.lat_column_param.col_index
        # filter input stream as much as possible:
        # - select useful columns only
        # - restrict to visible area
        stream = self.input_stream
        stream = stream.filter_column(lng_col_idx, operator.__ge__, westlng)
        stream = stream.filter_column(lng_col_idx, operator.__le__, eastlng)
        stream = stream.filter_column(lat_col_idx, operator.__ge__, southlat)
        stream = stream.filter_column(lat_col_idx, operator.__le__, northlat)
        return stream

    def minimal_stream(self):
        lng_col_idx, lat_col_idx = \
            self.lng_column_param.col_index, self.lat_column_param.col_index
        stream = self.current_filtered_stream
        stream = stream.select_columns(lng_col_idx, lat_col_idx)
        return stream

    def handle_event(self, event):
        if not self.input_stream.connected():
            return { 'issue': 'NO DATA: Input is not connected.' }
        ev_type = event[0]
        time_credit = event[1]
        if ev_type == 'map_move':
            info = event[2]
            # update current_filtered_stream
            self.current_filtered_stream = self.filtered_stream(**info)
            # get minimal stream (only 2 columns needed for the heatmap)
            stream = self.minimal_stream()
            # create heatmap
            self.curr_heatmap = HeatMap(stream, **info)
        # from now on, map_move or map_continue is the same thing
        # compute heatmap
        self.curr_heatmap.compute(time_credit)
        # return compressed form
        compressed_hm = self.curr_heatmap.compressed_form()
        return { 'heatmap': compressed_hm }
