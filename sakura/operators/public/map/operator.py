#!/usr/bin/env python
import itertools
from sakura.daemon.processing.operator import Operator
from sakura.daemon.processing.parameter import FloatColumnSelection

class MapOperator(Operator):
    NAME = "Map"
    SHORT_DESC = "Map display and selection operator."
    TAGS = [ "geo", "map", "selection" ]
    def construct(self):
        
        self.user_markers = []
        
        # inputs
        # TODO: final version should add this:
        self.input_markers = self.register_input('Markers')
        
        # internal streams
        markers = self.register_internal_stream('Markers', self.compute_markers)
        markers.add_column('longitude', float)
        markers.add_column('latitude', float)
        
        # parameters
        self.input_longitude_column = self.register_parameter('input longitude',
                FloatColumnSelection(self.input_markers))
        self.input_latitude_column = self.register_parameter('input latitude',
                FloatColumnSelection(self.input_markers))
        
        # additional tabs
        self.register_tab('Map', 'map.html')
    
    def compute_markers(self):
        input_markers = zip(self.input_longitude_column, self.input_latitude_column)
        all_markers = itertools.chain(input_markers, self.user_markers)
        visible_markers = filter(
                    lambda lnglat: \
                        self.lng_bounds[0] < lnglat[0] <self.lng_bounds[1] and \
                        self.lat_bounds[0] < lnglat[1] <self.lat_bounds[1],
                    all_markers)
        yield from visible_markers
    
    def handle_event(self, event):
        ev_type = event[0]
        if ev_type == 'map_clicked':
            latlng = event[1]
            self.user_markers.append((latlng['lng'], latlng['lat']))
        elif ev_type == 'map_move':
            southwest, northeast = event[1], event[2]
            self.lat_bounds = southwest['lat'], northeast['lat']
            self.lng_bounds = southwest['lng'], northeast['lng']
