#!/usr/bin/env python3
import numpy as np
import numpy.random
from time import time

class Markers:
    def __init__(self, lnglat):
        self.iterator = lnglat.chunks()
        # stream status parameters
        self.done = False
        self.latList = None
        self.lngList = None
    def compute(self, time_credit):
        # make histogram:
        # - create a pixel grid
        # - given a tuple (lng, lat) increment the corresponding pixel
        deadline = time() + time_credit
        deadline_reached = False
        for chunk in self.iterator:
            lng, lat = chunk.columns
            if time() > deadline:
                deadline_reached = True
                break
        if not deadline_reached:
            # we left the loop because of the end of iteration
            self.done = True
        self.latList = lat.tolist()
        self.lngList = lng.tolist()