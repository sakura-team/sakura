#!/usr/bin/env python
import itertools, numpy as np
from sakura.daemon.processing.operator import Operator
from sakura.daemon.processing.parameter import TagBasedColumnSelection
from .markers import Markers
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
        self.latList = None
        self.lngList = None
        self.length = 0
        self.done = False

    def check_point_inside(self, x, y, polygon):
        res = False
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

    def filtered_stream(self):
        # get columns selected in combo parameters
        lng_column, lat_column = \
            self.lng_column_param.value, self.lat_column_param.value
        # filter input stream as much as possible:
        # - select useful columns only
        # - restrict to visible area
        stream = self.input_stream
        stream = stream.select_columns(lng_column, lat_column)
        #stream = stream.filter(self.check_point_inside(lat_column, lng_column, polygon))
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

        if ev_type == "polygons_update":
            polygon = event[1]
            stream = self.filtered_stream()
            for chunk in stream.chunks():
                lng, lat = chunk.columns
            
            list_lat = lat.tolist()
            list_lng = lng.tolist()
            markers = []
            for j in range(0,len(polygon)):
                markers.append([])
            for i in range(0,len(list_lat)):
                for j in range(0, len(polygon)):
                    if self.check_point_inside(list_lat[i], list_lng[i], polygon[j]):
                        markers[j].append([list_lat[i], list_lng[i]])

        return {'tweetsmap': markers}

            