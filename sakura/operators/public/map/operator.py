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
        self.input_longitude_column = self.register_parameter('input longitude',
                TagBasedColumnSelection(self.input_markers, 'longitude'))
        self.input_latitude_column = self.register_parameter('input latitude',
                TagBasedColumnSelection(self.input_markers, 'latitude'))
        # additional tabs
        self.register_tab('Map', 'map.html')

    def flat_iterator(self):
        lng_idx = self.input_longitude_column.index
        lat_idx = self.input_latitude_column.index
        for t in self.input_markers:
            yield t[lng_idx]
            yield t[lat_idx]

    def handle_event(self, event):
        ev_type = event[0]
        if ev_type == 'map_clicked':
            #latlng = event[1]
            pass
        elif ev_type == 'map_move':
            info = event[1]
            self.lat_bounds = info['southlat'], info['northlat']
            self.lng_bounds = info['westlng'], info['eastlng']
            t0 = time()
            lnglat = np.fromiter(self.flat_iterator(), np.float)
            t1 = time()
            lnglat = lnglat.reshape(int(lnglat.size/2), 2).T
            print('  collect: %.4f' % (t1 - t0))
            info['lnglat'] = lnglat
            return { 'heatmap': heatmap.generate(**info) }
