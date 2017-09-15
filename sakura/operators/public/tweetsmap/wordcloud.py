#!/usr/bin/env python3
import numpy as np
import numpy.random
from math import sin, cos, sqrt, atan2, radians
from .polygonfilter import check_point_inside, check_contained_words
from wordcloud import WordCloud, STOPWORDS
import base64
from stop_words import get_stop_words
# import matplotlib.path as mpltPath
# from shapely.geometry import Point
# from shapely.geometry.polygon import Polygon
from time import time

# web mercator projection functions
# ---------------------------------

class WordCloudInfo:
    def __init__(self, stream, polygon, timeStart, timeEnd, words):
        self.stream = stream
        self.iterator = stream.chunks(chunk_size=1000)
        self.polygon = polygon
        self.text = ''
        self.timeStart = timeStart
        self.timeEnd = timeEnd
        self.count = 0
        # prepare compression parameters
        self.done = False
        self.words = words
    def compute(self, time_credit):
        # make histogram:
        # - create a pixel grid
        # - given a tuple (lng, lat) increment the corresponding pixel
        deadline = time() + time_credit
        deadline_reached = False
        for chunk in self.iterator:
            list = chunk.tolist()
            for i in range(len(list)):
                col = list[i]
                if len(self.polygon) == 0:
                    pass
                else:
                    if (col[2] > self.timeEnd) or (col[2] < self.timeStart):
                        pass
                    elif check_contained_words(col[3], self.words) and check_point_inside(col[1], col[0], self.polygon):
                        self.text += col[3]
                        self.count += 1
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
        data = []
        if self.text !='' :
            stopwords = set(STOPWORDS)
            stopwords.update(['https', 'co'])
            stopwords.update(get_stop_words('french'))
            w = WordCloud(max_words=200, stopwords = stopwords)
            words = w.generate(self.text).words_
            for word in words:
                data.append([word, words[word]])
        return dict(
            data = data,
            count = self.count,
            done = self.done
        )
        
