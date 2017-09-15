#!/usr/bin/env python3
import numpy as np
import numpy.random
from math import sin, cos, sqrt, atan2, radians
from .polygonfilter import check_point_inside, check_contained_words
# import matplotlib.path as mpltPath
# from shapely.geometry import Point
# from shapely.geometry.polygon import Polygon
from time import time

# web mercator projection functions
# ---------------------------------

class Exportation:
    def __init__(self, stream, polygon, timeStart, timeEnd, listWords):
        self.stream = stream
        self.iterator = stream.chunks(chunk_size=1000)
        self.exportation = None
        self.polygon = polygon
        self.timeStart = timeStart
        self.timeEnd = timeEnd
        self.listWords = listWords
        # prepare compression parameters
        self.done = False
    def compute(self, time_credit):
        # make histogram:
        # - create a pixel grid
        # - given a tuple (lng, lat) increment the corresponding pixel
        deadline = time() + time_credit
        deadline_reached = False
        self.exportation = None
        for chunk in self.iterator:
            list = chunk.tolist()
            deletedIndex = []
            for i in range(len(list)):
                col = list[i]
                if len(self.polygon) == 0:
                    pass
                else:
                    deleted = True
                    for j in range(0,len(self.polygon)):
                        if (col[2] > self.timeEnd[j]) or (col[2] < self.timeStart[j]):
                            pass
                        elif check_contained_words(col[3], self.listWords[j]) and check_point_inside(col[1], col[0], self.polygon[j]):
                            deleted = False
                            break
                    if deleted :
                        deletedIndex.append(i)
            chunk_exportation = np.delete(chunk, deletedIndex, None);
            if self.exportation is None:
                self.exportation = chunk_exportation
            else :
                self.exportation = np.append(self.exportation,chunk_exportation)
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
        # count = int(self.exportation.size)
        # print(len(self.exportation.tolist()));
        # import pdb
        # pdb.set_trace()
        data = {}
        data['key'] = []
        for column in self.stream.columns:
            data['key'].append(column.label)
        data['list'] = self.exportation;
        return dict(
            data = data,
            # count = count,
            done = self.done
        )
        
