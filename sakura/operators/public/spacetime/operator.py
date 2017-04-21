#!/usr/bin/env python
import itertools, numpy as np
from sakura.daemon.processing.operator import Operator
from sakura.daemon.processing.parameter import TagBasedColumnSelection
from time import time

class SpaceTimeOperator(Operator):
    NAME = "SpaceTime"
    SHORT_DESC = "SpaceTime displays geolocalized paths in 3D."
    TAGS = [ "geo", "map", "gpx", "3D" ]
    def construct(self):
        pass
        # additional tabs
        self.register_tab('3D', 'spacetime.html')
    
    def flat_iterator(self):
        pass
    
    def handle_event(self, event):
        ev_type = event[0]
        if ev_type == 'click':
            pass