#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#Michael ORTEGA - 26/Avril/2019

import geojson  as gj
import numpy    as np

class geo_shape:
    def __init__(self, name, points):
        self.name   = name
        self.points = points
        self.triangles = []

    def triangulate(self):
        def _strip_range(stop):
            '''sort verticies in triangle strip order, i.e. 0 -1 1 -2 2 ...'''
            i = 0
            while i < stop:
                i += 1
                v, s = divmod(i, 2)
                yield v*(s*2-1)

        for i in _strip_range(len(self.points)):
            self.triangles.append(self.points[i])

class geo_shapes:
    def __init__(self):
        self.shapes         = []
        self.displayed      = True

    def read_shapes(self, fname):
        if fname:
            geoj = gj.load(open(fname, 'r'))

            for f in geoj['features']:
                n = f['properties']['name']
                c = f['geometry']['coordinates']
                out = []

                #-------------
                #for now we only deal with the contours, no holes
                while len(c) > 1:
                    c = c[0]
                #--------------

                while len(c) > 0:
                    elem = c.pop()
                    if isinstance(elem, list):
                        for e in elem:
                            c.append(e)
                    else:
                        out.append(elem)

                out.reverse()
                out = np.reshape(np.array(out), (-1, 2))
                fs = geo_shape(n, out)
                self.shapes.append(fs)
                fs.triangulate()
