#!/usr/bin/env python
import itertools, numpy as np
from sakura.daemon.processing.operator import Operator
from sakura.daemon.processing.parameter import TagBasedColumnSelection
from .heatmap import HeatMap
from time import time
from sakura.daemon.processing.stream import SimpleStream


class MapOperator(Operator):
    NAME = "Map"
    SHORT_DESC = "Map display and selection operator."
    TAGS = [ "geo", "map", "selection" ]
    def construct(self):
        # inputs
        self.input_stream = self.register_input('GPS data')
        # parameters
        self.lng_column_param = self.register_parameter('input longitude',
                TagBasedColumnSelection(self.input_stream, 'longitude'))
        self.lat_column_param = self.register_parameter('input latitude',
                TagBasedColumnSelection(self.input_stream, 'latitude'))
        
        self.output = self.register_output(
                    SimpleStream('Filtred data', self.compute))
        self.output.add_column('lat', float)
        self.output.add_column('lng', float)

        # additional tabs
        self.register_tab('Map', 'map.html')
        # custom attributes
        self.curr_heatmap = None

    def filtered_stream(self, westlng, eastlng, southlat, northlat, **args):
        # get columns selected in combo parameters
        lng_column, lat_column = \
            self.lng_column_param.value, self.lat_column_param.value
        # filter input stream as much as possible:
        # - select useful columns only
        # - restrict to visible area
        stream = self.input_stream
        stream = stream.select_columns(lng_column, lat_column)
        stream = stream.filter(lng_column >= westlng)
        stream = stream.filter(lng_column <= eastlng)
        stream = stream.filter(lat_column >= southlat)
        stream = stream.filter(lat_column <= northlat)
        return stream

    def compute(self):
        print('ook')
        lng_column, lat_column = \
            self.lng_column_param.value, self.lat_column_param.value
        stream = self.temp
        for chunk in stream.chunks():
            list = chunk.tolist()
            # for i in range(0, len(chunk.tolist())
            for i in range(len(list)):
                col = list[i]
                if col[0]>42.2:
                    yield col
    def handle_event(self, event):
        if not self.input_stream.connected():
            return { 'issue': 'NO DATA: Input is not connected.' }
        ev_type = event[0]
        time_credit = event[1]
        if ev_type == 'map_move':
            info = event[2]
            stream = self.filtered_stream(**info)
            self.temp = stream
            stream = SimpleStream('Mean result', self.compute)
            stream.add_column('lat', float)
            stream.add_column('lng', float)
            # self.register_output(stream)
            # stream.length = 100;
            # create heatmap
            self.curr_heatmap = HeatMap(stream, **info)
        # from now on, map_move or map_continue is the same thing
        # compute heatmap
        self.curr_heatmap.compute(time_credit)
        # return compressed form
        compressed_hm = self.curr_heatmap.compressed_form()
        return { 'heatmap': compressed_hm }
