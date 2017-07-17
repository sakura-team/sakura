#!/usr/bin/env python
import itertools, numpy as np
from sakura.daemon.processing.operator import Operator
from sakura.daemon.processing.parameter import TagBasedColumnSelection
from .markers import Markers
from time import time
from math import sin, cos, sqrt, atan2, radians
import matplotlib.path as mpltPath
from time import time
import shapely
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

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
        self.latList = None
        self.lngList = None
        self.length = 0
        self.done = False
    
    def distance(self, lat1, lng1, lat2, lng2):
        radius = 6371 * 1000

        lat1 = radians(lat1)
        lat2 = radians(lat2)
        lng1 = radians(lng1)
        lng2 = radians(lng2)

        dlng = lng2 - lng1
        dlat = lat2 - lat1

        a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlng/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))

        return radius*c

    def check_point_inside(self, x, y, polygonInfo):
        typePoly = polygonInfo['type']
        res = False
        if typePoly == 'polygon':
            polygon = polygonInfo['data']
            start_time = time()
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
                
                    intersect = ((yi>y) != (yj >y)) and (x < ((xj - xi)*(y -yi)/(yj -yi)+xi))
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
            res = self.distance(x, y, x_center, y_center) < radius

        return res

    def filtered_stream(self, polygon):
        def check_point( x, y, **kwds):
            polygonInfo = kwds['poly']
            typePoly = polygonInfo['type']
            res = False
            if typePoly == 'polygon':
                polygon = polygonInfo['data']
                start_time = time()
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
                
                        intersect = ((yi>y) != (yj >y)) and (x < ((xj - xi)*(y -yi)/(yj -yi)+xi))
                        if intersect:
                            res = not res
                        j = i
                        i += 1
            return res
        # get columns selected in combo parameters
        lng_column, lat_column = \
                self.lng_column_param.value, self.lat_column_param.value
        # filter input stream as much as possible:
        # - select useful columns only
        stream = self.input_stream
        stream = stream.select_columns(lng_column, lat_column)
        return stream
            
    def handle_event(self, event):
        # ev_type = event[0]
        # time_credit = event[1]
        
        # if ev_type == 'new_zone':
        #     stream = self.filtered_stream()
        #     self.curr_markers = Markers(stream)
        
        # self.curr_markers.compute(time_credit)

        # return { 'tweetsmap': dict(lat = self.curr_markers.latList, lng = self.curr_markers.lngList , done = self.curr_markers.done) }
        ev_type = event[0]
        time_credit = event[1]
        polygon = event[2]

        if ev_type == "polygons_update":
            stream = self.filtered_stream(polygon)
            self.curr_markers = Markers(stream)

        self.curr_markers.compute(time_credit)
            
        list_lat = self.curr_markers.latList
        list_lng = self.curr_markers.lngList
        markers = []
        for j in range(0,len(polygon)):
            markers.append([])
        for i in range(0,len(list_lat)):
            for j in range(0, len(polygon)):
                if self.check_point_inside(list_lat[i], list_lng[i], polygon[j]):
                    markers[j].append([list_lat[i], list_lng[i]])

        return {'tweetsmap': markers, 'done': self.curr_markers.done}

            