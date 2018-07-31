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
        self.input_plug = self.register_input('GPS data')
        # outputs
        self.output_plug = self.register_output('Filtered GPS data')
        # parameters
        self.lng_column_param = self.register_parameter(
                TagBasedColumnSelection('input longitude', self.input_plug, 'longitude'))
        self.lat_column_param = self.register_parameter(
                TagBasedColumnSelection('input latitude', self.input_plug, 'latitude'))
        # additional tabs
        self.register_tab('Map', 'map.html')
        # custom attributes
        self.curr_heatmap = None

    def geo_filter(self, source, westlng, eastlng, southlat, northlat, **args):
        """restrict source to visible area"""
        # get columns selected in combo parameters
        lng_col_idx, lat_col_idx = \
            self.lng_column_param.col_index, self.lat_column_param.col_index
        # apply filters
        source = source.filter_column(lng_col_idx, operator.__ge__, westlng)
        source = source.filter_column(lng_col_idx, operator.__le__, eastlng)
        source = source.filter_column(lat_col_idx, operator.__ge__, southlat)
        source = source.filter_column(lat_col_idx, operator.__le__, northlat)
        return source

    def columns_filter(self, source):
        """restrict source to latitude and longitude columns"""
        lng_col_idx, lat_col_idx = \
            self.lng_column_param.col_index, self.lat_column_param.col_index
        source = source.select_columns(lng_col_idx, lat_col_idx)
        return source

    def handle_event(self, event):
        if not self.input_plug.connected():
            return { 'issue': 'NO DATA: Input is not connected.' }
        ev_type = event[0]
        time_credit = event[1]
        if ev_type == 'map_move':
            info = event[2]
            # update current source...
            source = self.input_plug.source
            source = self.geo_filter(source, **info)
            # ...on output plug
            self.output_plug.source = source
            # ...for heatmap calculation
            heatmap_source = self.columns_filter(source)
            # create heatmap
            self.curr_heatmap = HeatMap(heatmap_source, **info)
        # from now on, map_move or map_continue is the same thing
        # compute heatmap
        self.curr_heatmap.compute(time_credit)
        # return compressed form
        compressed_hm = self.curr_heatmap.compressed_form()
        return { 'heatmap': compressed_hm }
