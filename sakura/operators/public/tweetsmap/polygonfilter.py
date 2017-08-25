#!/usr/bin/env python3
# import numpy as np
# import numpy.random
from math import sin, cos, sqrt, atan2, radians
# import matplotlib.path as mpltPath
# from shapely.geometry import Point
# from shapely.geometry.polygon import Polygon
# from time import time

# web mercator projection functions
# ---------------------------------


def distance(lat1, lng1, lat2, lng2):
    radius = 6371 * 1000

    lat1 = radians(lat1)
    lat2 = radians(lat2)
    lng1 = radians(lng1)
    lng2 = radians(lng2)

    dlng = lng2 - lng1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlng / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return radius * c


def check_point_inside(x, y, polygonInfo):
    typePoly = polygonInfo['type']
    res = False
    if typePoly == 'polygon':
        polygon = polygonInfo['data']
        # start_time = time()
        for ii in range(0, len(polygon)):
            polyPoints = polygon[ii]
            i = 0
            j = len(polyPoints) - 1
            while(True):
                if i >= len(polyPoints):
                    break
                xi = polyPoints[i][0]
                yi = polyPoints[i][1]
                xj = polyPoints[j][0]
                yj = polyPoints[j][1]

                intersect = ((yi > y) != (yj > y)) and (x < ((xj - xi) * (y - yi) / (yj - yi) + xi))
                if intersect:
                    res = not res
                j = i
                i += 1
        # print(" ALG : %0.9f" % (time() - start_time))
            # start_time = time()
            # path = Polygon(polygon[0])
            # res = path.contains(Point(x,y))
            # print(" MPLT : %0.9f" % (time() - start_time))
    elif typePoly == 'circle':
        circle = polygonInfo['data']
        x_center = circle['center']['lat']
        y_center = circle['center']['lng']
        radius = circle['radius']
        # check if a point is inside a circle
        res = distance(x, y, x_center, y_center) < radius
    return res
