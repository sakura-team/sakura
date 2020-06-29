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
        self.output_plug = self.register_output('Filtered GPS data',
                                    explain_disabled = self.explain_disabled_output)
        # parameters
        self.lng_column_param = self.register_parameter(
                'TAG_BASED_COLUMN_SELECTION', 'input longitude', self.input_plug, 'longitude')
        self.lng_column_param.on_change.subscribe(self.update_map_and_output)
        self.lat_column_param = self.register_parameter(
                'TAG_BASED_COLUMN_SELECTION', 'input latitude', self.input_plug, 'latitude')
        self.lat_column_param.on_change.subscribe(self.update_map_and_output)
        # additional tabs
        self.register_tab('Map', 'map.html')
        # custom attributes
        self.curr_heatmap = None
        # map display info
        self.map_info = None

    def explain_disabled_output(self):
        if self.input_plug.source is None:
            return 'NO DATA: map operator input is not connected.'
        elif self.lng_column_param.column is None or self.lat_column_param.column is None:
            return 'NO DATA: operator parameters are not set.'
        elif self.map_info is None:
            return "NO DATA: select a geographic region by using the 'Map' tab."
        else:   # other reason (quite unexpected)
            return "NO DATA: operator did not publish data yet."

    def geo_filter(self, source, lng_column, lat_column,
                   westlng, eastlng, southlat, northlat, **args):
        """restrict source to visible area"""
        source = source.where((lng_column >= westlng)  &
                              (lng_column <= eastlng)  &
                              (lat_column >= southlat) &
                              (lat_column <= northlat))
        return source

    def update_map_and_output(self):
        lng_column = self.lng_column_param.column
        lat_column = self.lat_column_param.column
        if lng_column is None or lat_column is None or self.map_info is None:
            self.output_plug.source = None
            self.curr_heatmap = None
            return
        # update current source...
        source = self.input_plug.source
        source = self.geo_filter(source, lng_column, lat_column, **self.map_info)
        # ...on output plug
        self.output_plug.source = source
        # ...for heatmap calculation (keep only lng and lat columns)
        heatmap_source = source.select(lng_column, lat_column)
        # create heatmap
        self.curr_heatmap = HeatMap(heatmap_source, **self.map_info)

    def handle_event(self, ev_type, time_credit, **info):
        if ev_type == 'map_move':
            self.map_info = info
            self.update_map_and_output()
        if self.curr_heatmap is None:
            return { 'issue': self.explain_disabled_output() }
        # from now on, map_move or map_continue is the same thing
        # compute heatmap
        self.curr_heatmap.compute(time_credit)
        # return compressed form
        compressed_hm = self.curr_heatmap.compressed_form()
        return { 'heatmap': compressed_hm }
