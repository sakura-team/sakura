#!/usr/bin/env python
import itertools, numpy as np
from sakura.daemon.processing.operator import Operator
from sakura.daemon.processing.parameter import TagBasedColumnSelection
from time import time

class TweetsOperator(Operator):
    NAME = "Tweetsmap"
    SHORT_DESC = "Tweets display and selection operator."
    TAGS = [ "geo", "map", "selection" ]
    def construct(self):
        # inputs
        self.input_stream = self.register_input('GPS data')
        # parameters
        self.lng_column_param = self.register_parameter('input longitude',
                TagBasedColumnSelection(self.input_stream, 'longitude'))
        self.lat_column_param = self.register_parameter('input latitude',
                TagBasedColumnSelection(self.input_stream, 'latitude'))
        # additional tabs
        self.register_tab('Tweetsmap', 'index.html')

    def handle_event(self, event):
        ev_type = event[0]
        if ev_type == 'new_zone':
            lng_column, lat_column = \
                self.lng_column_param.value, self.lat_column_param.value
            stream = self.input_stream
            stream = stream.select_columns(lng_column,lat_column)
            for chunk in stream.chunks():
                 lng, lat = chunk.columns
            return { 'tweetsmap': dict(lat = lat.tolist(), lng = lng.tolist()) }
            
