#!/usr/bin/env python3
import numpy as np
import numpy.random
from time import time

# web mercator projection functions
# ---------------------------------
DEG_TO_RAD = 1 / (180 / np.pi)

def linear_lat(lat, atanh = np.arctanh, sin = np.sin, alpha = DEG_TO_RAD):
    return atanh(sin(lat * alpha))

def inv_linear_lat(ll, asin = np.arcsin, tanh = np.tanh, beta = 1 / DEG_TO_RAD):
    return asin(tanh(ll)) * beta

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
def generate(lnglat, width, height, westlng, eastlng, southlat, northlat):
    t0 = time()
    # compute pixel bounds of the map
    x = np.append(np.arange(0, width, 5), width)
    y = np.append(np.arange(0, height, 5), height)
    # project pixel bounds coordinates (x, y -> lng, lat)
    edgelng = x_to_lng(width, westlng, eastlng, x)
    centerlng = x_to_lng(width, westlng, eastlng, (x[1:] + x[:-1])/2)
    edgelat = y_to_lat(height, southlat, northlat, y)
    centerlat = y_to_lat(height, southlat, northlat, (y[1:] + y[:-1])/2)
    # convert to x, y
    if lnglat.size == 0:
        lng, lat = np.empty(0), np.empty(0)
    else:
        lng, lat = lnglat[0], lnglat[1]
    t1 = time()
    # make histogram:
    # - create a pixel grid
    # - given a tuple (lng, lat) increment the corresponding pixel
    heatmap = np.histogram2d(lng, lat, bins=(edgelng, edgelat), range=((westlng, eastlng), (southlat, northlat)))[0]
    heatmap = heatmap.T
    t2 = time()
    # apply threshold
    nzhm = (heatmap / heatmap.max()) > 0.05
    # get sparse matrix representation: (lat, lng, intensity) tuples.
    # in order to lower network usage, we will transfer this data in a
    # compressed form: lng & lat values will be transfered as integers
    # together with a scaling factor and an offset to be applied.
    scalelat = (edgelat[1:] - edgelat[:-1]).min() / 2
    approx_centerlat = numpy.rint((centerlat - centerlat[0]) / scalelat)
    scalelng = edgelng[1] - edgelng[0]     # longitude is linear
    approx_centerlng = numpy.rint((centerlng - centerlng[0]) / scalelng)
    result = dict(
        data = dict(
                lat = approx_centerlat[nzhm.nonzero()[0]].astype(int).tolist(),
                lng = approx_centerlng[nzhm.nonzero()[1]].astype(int).tolist(),
                val = heatmap[nzhm].astype(int).tolist()
        ),
        scales = dict(lat=scalelat, lng=scalelng),
        offsets = dict(lat=centerlat[0], lng=centerlng[0])
    )
    t3 = time()
    print('  project: %.4f' % (t1 - t0))
    print('histogram: %.4f' % (t2 - t1))
    print(' compress: %.4f' % (t3 - t2))
    return result
