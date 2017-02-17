#!/usr/bin/env python
from itertools import islice
from sakura.daemon.processing.operator import Operator
from sakura.daemon.processing.parameter import FloatColumnSelection

class MapOperator(Operator):
    NAME = "Map"
    SHORT_DESC = "Map display and selection operator."
    TAGS = [ "geo", "map", "selection" ]
    def construct(self):
        
        #for testing
        self.index = 0
        
        # inputs
        # TODO: final version should add this:
        self.input_markers = self.register_input('Markers')
        
        # internal streams
        markers = self.register_internal_stream('Markers', self.compute_markers)
        markers.add_column('GeoJSON', str)
        
        # parameters
        self.input_longitude_column = self.register_parameter('input longitude',
                FloatColumnSelection(self.input_markers))
        self.input_latitude_column = self.register_parameter('input latitude',
                FloatColumnSelection(self.input_markers))
        
        # additional tabs
        self.register_tab('Map', 'map.html')
    
    def compute_markers(self):
        yield from islice(
                zip(self.input_longitude_column, self.input_latitude_column),
                self.index,
                None)
    
    def handle_event(self, e):
        self.index += 1
        print("New index:", self.index)
