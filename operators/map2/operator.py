#!/usr/bin/env python
import itertools, numpy as np, operator
from sakura.daemon.processing.operator import Operator
from .heatmap import HeatMap
from time import time

class Map2Operator(Operator):
    NAME = "Map2"
    SHORT_DESC = "Map2 display and selection operator."
    TAGS = [ "geo", "map", "selection" ]
    def construct(self):
        # inputs
        self.input_plug = self.register_input('GPS data')
        # outputs
        self.output_plug = self.register_output('Filtered GPS data')
        # parameters
        self.geo_column_param = self.register_parameter(
                'GEOMETRY_COLUMN_SELECTION', 'geo column', self.input_plug)
        # additional tabs
        self.register_tab('Map', 'map.html')
        # custom attributes
        self.curr_heatmap = None

    def handle_event(self, ev_type, time_credit, **info):
        if not self.input_plug.connected():
            return { 'issue': 'NO DATA: Input is not connected.' }
        if ev_type == 'map_move':
            # we have to update current source
            source = self.input_plug.source
            geo_column = self.geo_column_param.column
            # * first, restrict source to visible area
            source = source.where((geo_column.X >= info['westlng'])  &
                                  (geo_column.X <= info['eastlng'])  &
                                  (geo_column.Y >= info['southlat']) &
                                  (geo_column.Y <= info['northlat']))
            # * update output plug source
            self.output_plug.source = source
            # * update source of heatmap calculation
            #   (it needs geometry columns only)
            heatmap_source = source.select(geo_column.X, geo_column.Y)
            # * create heatmap
            self.curr_heatmap = HeatMap(heatmap_source, **info)
        # from now on, map_move or map_continue is the same thing
        # compute heatmap
        self.curr_heatmap.compute(time_credit)
        # return compressed form
        compressed_hm = self.curr_heatmap.compressed_form()
        return { 'heatmap': compressed_hm }
