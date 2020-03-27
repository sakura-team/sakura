#!/usr/bin/env python3
import numpy as np
import numpy.random
from time import time

# web mercator projection functions
# ---------------------------------
def linear_lat(lat, atanh = np.arctanh, sin = np.sin, radians = np.radians):
    return atanh(sin(radians(lat)))

def inv_linear_lat(ll, asin = np.arcsin, tanh = np.tanh, degrees = np.degrees):
    return degrees(asin(tanh(ll)))

def lng_to_x(w, lng_min, lng_max, lng):
    return (lng - lng_min) * (w / (lng_max - lng_min))

def lat_to_y(h, lat_min, lat_max, lat):
    return (linear_lat(lat) - linear_lat(lat_min)) * (h / (linear_lat(lat_max) - linear_lat(lat_min)))

def x_to_lng(w, lng_min, lng_max, x):
    return x * ((lng_max - lng_min)/w) + lng_min

def y_to_lat(h, lat_min, lat_max, y):
    return inv_linear_lat(y * ((linear_lat(lat_max) - linear_lat(lat_min))/h) + linear_lat(lat_min))

# heatmap data generation
# -----------------------
class HeatMap:
    def __init__(self, lnglat, width, height, westlng, eastlng, southlat, northlat):
        # compute pixel bounds of the map
        x = np.append(np.arange(0, width, 5), width)
        y = np.append(np.arange(0, height, 5), height)
        # project pixel bounds coordinates (x, y -> lng, lat)
        edgelng = x_to_lng(width, westlng, eastlng, x)
        centerlng = x_to_lng(width, westlng, eastlng, (x[1:] + x[:-1])/2)
        edgelat = y_to_lat(height, southlat, northlat, y)
        centerlat = y_to_lat(height, southlat, northlat, (y[1:] + y[:-1])/2)
        # prepare computation parameters
        self.bins = edgelng, edgelat
        self.range = (westlng, eastlng), (southlat, northlat)
        self.iterator = lnglat.chunks()
        self.heatmap = None
        # prepare compression parameters
        scalelat = (edgelat[1:] - edgelat[:-1]).min() / 2
        self.approx_centerlat = numpy.rint((centerlat - centerlat[0]) / scalelat)
        scalelng = edgelng[1] - edgelng[0]     # longitude is linear
        self.approx_centerlng = numpy.rint((centerlng - centerlng[0]) / scalelng)
        self.scales = dict(lat=scalelat, lng=scalelng)
        self.offsets = dict(lat=centerlat[0], lng=centerlng[0])
        # stream status parameters
        self.done = False
    def compute(self, time_credit):
        # make histogram:
        # - create a pixel grid
        # - given a tuple (lng, lat) increment the corresponding pixel
        deadline = time() + time_credit
        deadline_reached = False
        for chunk in self.iterator:
            lng, lat = chunk.columns
            chunk_heatmap = np.histogram2d(lng, lat, bins=self.bins, range=self.range)[0]
            if self.heatmap is None:
                self.heatmap = chunk_heatmap.T
            else:
                self.heatmap += chunk_heatmap.T
            if time() > deadline:
                deadline_reached = True
                break
        if not deadline_reached:
            # we left the loop because of the end of iteration
            self.done = True
    # get sparse matrix representation: (lat, lng, intensity) tuples.
    # in order to lower network usage, we will transfer this data in a
    # compressed form: lng & lat values will be transfered as integers
    # together with a scaling factor and an offset to be applied.
    def compressed_form(self):
        # count number of points
        count = int(self.heatmap.sum())
        if count == 0:
            # if no points, return empty data
            data = dict(lat = [], lng = [], val = [])
        else:
            # apply threshold and
            # compute approximated sparse matrix data
            nonzero_xy = ((self.heatmap / self.heatmap.max()) > 0.05).nonzero()
            nonzero_x = nonzero_xy[1]
            nonzero_y = nonzero_xy[0]
            data = dict(
                    lat = self.approx_centerlat[nonzero_y].astype(int).tolist(),
                    lng = self.approx_centerlng[nonzero_x].astype(int).tolist(),
                    val = self.heatmap[nonzero_xy].astype(int).tolist()
            )
        return dict(
            data = data,
            scales = self.scales,
            offsets = self.offsets,
            count = count,
            done = self.done
        )
