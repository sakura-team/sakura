#!/usr/bin/env python
import itertools, numpy as np, operator
from sakura.daemon.processing.operator import Operator
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
                'TAG_BASED_COLUMN_SELECTION', 'input longitude', self.input_plug, 'longitude')
        self.lat_column_param = self.register_parameter(
                'TAG_BASED_COLUMN_SELECTION', 'input latitude', self.input_plug, 'latitude')
        # additional tabs
        self.register_tab('Map', 'map.html')
        # custom attributes
        self.curr_heatmap = None

    def geo_filter(self, source, lng_column, lat_column,
                   westlng, eastlng, southlat, northlat, **args):
        """restrict source to visible area"""
        source = source.where((lng_column >= westlng)  &
                              (lng_column <= eastlng)  &
                              (lat_column >= southlat) &
                              (lat_column <= northlat))
        return source

    def handle_event(self, ev_type, time_credit, **info):
        if not self.input_plug.connected():
            return { 'issue': 'NO DATA: Input is not connected.' }
        if ev_type == 'map_move':
            # update current source...
            source = self.input_plug.source
            lng_column = self.lng_column_param.column
            lat_column = self.lat_column_param.column
            source = self.geo_filter(source, lng_column, lat_column, **info)
            # ...on output plug
            self.output_plug.source = source
            # ...for heatmap calculation (keep only lng and lat columns)
            heatmap_source = source.select(lng_column, lat_column)
            # create heatmap
            self.curr_heatmap = HeatMap(heatmap_source, **info)
        # from now on, map_move or map_continue is the same thing
        # compute heatmap
        self.curr_heatmap.compute(time_credit)
        # return compressed form
        compressed_hm = self.curr_heatmap.compressed_form()
        return { 'heatmap': compressed_hm }
