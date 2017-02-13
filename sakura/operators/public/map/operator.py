#!/usr/bin/env python
from sakura.daemon.processing.operator import Operator
from sakura.daemon.processing.parameter import StrColumnSelection

# TODO: final version should remove the following
SAMPLE_POINTS = """\
{"type":"Point","coordinates":[31.165342,30.010138]}
{"type":"Point","coordinates":[-70.693406,19.46907]}
{"type":"Point","coordinates":[-63.8533,10.95622]}
{"type":"Point","coordinates":[103.31764,3.864095]}
{"type":"Point","coordinates":[112.745337,-7.277814]}
{"type":"Point","coordinates":[-51.225596,-30.040125]}
{"type":"Point","coordinates":[40.223849,37.919347]}
{"type":"Point","coordinates":[-98.190736,19.039094]}
{"type":"Point","coordinates":[139.638216,35.549026]}
{"type":"Point","coordinates":[-46.684644,-23.564315]}
""".splitlines()

class MapOperator(Operator):
    NAME = "Map"
    SHORT_DESC = "Map display and selection operator."
    TAGS = [ "geo", "map", "selection" ]
    def construct(self):
        # inputs
        # TODO: final version should add this:
        #self.input_markers = self.register_input('Markers')

        # outputs
        markers = self.register_internal_stream('Markers', self.compute_markers)
        markers.add_column('GeoJSON', str)

        # parameters
        # TODO: final version should add this:
        #self.input_markers_column = self.register_parameter('GeoJSON markers column',
        #        StrColumnSelection(self.input_markers))

        # additional tabs
        self.register_tab('Map', 'js/map.js')

    def compute_markers(self):
        # TODO: final version should be:
        #for val in self.input_markers_column:
        #    yield (val,)
        for geojson in SAMPLE_POINTS:
            yield (geojson,)
