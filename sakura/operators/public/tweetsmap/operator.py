#!/usr/bin/env python
import itertools, numpy as np
from sakura.daemon.processing.operator import Operator
from sakura.daemon.processing.parameter import TagBasedColumnSelection
# from sakura.daemon.processing.parameter import NumericColumnSelection, StrColumnSelection
from sakura.daemon.processing.stream import SimpleStream
# from .markers import Markers
from time import time
from math import sin, cos, sqrt, atan2, radians
import matplotlib.path as mpltPath
import shapely
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from .heatmap import HeatMap
from .exportation import Exportation
from .wordcloud import WordCloudInfo

class TweetsOperator(Operator):
    NAME = 'Tweets'
    SHORT_DESC = 'Twitter Data Visualization.'
    TAGS = ["geo", "map", "selection"]
    def construct(self):
        # inputs
        self.input_stream = self.register_input('GPS data')
        # parameters
        self.lng_column_param = self.register_parameter('input longitude',
                TagBasedColumnSelection(self.input_stream, 'longitude'))
        self.lat_column_param = self.register_parameter('input latitude',
                TagBasedColumnSelection(self.input_stream, 'latitude'))
        self.time_column_param = self.register_parameter('input timestamp',
                TagBasedColumnSelection(self.input_stream, 'timestamp'))
        self.text_column_param = self.register_parameter('input text',
                TagBasedColumnSelection(self.input_stream, 'text'))
        # self.output = self.register_output(
        #             SimpleStream('Filtred by polygon', self.compute))
        # self.output.add_column('lat', float)
        # self.output.add_column('lng', float)

        # additional tabs
        self.register_tab('Map', 'index.html')
        # custom attributes
        self.curr_heatmap = None

             
    def filtered_stream(self, westlng, eastlng, southlat, northlat, disable, **args):
        # get columns selected in combo parameters
        lng_column, lat_column, time_column = \
            self.lng_column_param.value, self.lat_column_param.value, self.time_column_param.value
        # filter input stream as much as possible:
        # - select useful columns only
        # - restrict to visible area
        stream = self.input_stream
        stream = stream.select_columns(lng_column, lat_column, time_column)
        # import pdb
        # pdb.set_trace()
        stream = stream.filter(lng_column >= westlng)
        stream = stream.filter(lng_column <= eastlng)
        stream = stream.filter(lat_column >= southlat)
        stream = stream.filter(lat_column <= northlat)
        if disable :
            stream = stream.filter(lat_column > northlat)
        return stream
    def filtered2_stream(self, westlng, eastlng, southlat, northlat, **args):
        # get columns selected in combo parameters
        lng_column, lat_column, text_column, time_column = \
            self.lng_column_param.value, self.lat_column_param.value, self.text_column_param.value, self.time_column_param.value
        # filter input stream as much as possible:
        # - select useful columns only
        # - restrict to visible area
        stream = self.input_stream
        stream = stream.select_columns(lng_column, lat_column, text_column, time_column)
        stream = stream.filter(lng_column >= westlng)
        stream = stream.filter(lng_column <= eastlng)
        stream = stream.filter(lat_column >= southlat)
        stream = stream.filter(lat_column <= northlat)
        return stream
    # def compute(self):
    #     stream = self.filtered_stream(**self.info)
    #     for chunk in stream.chunks():
    #         list = chunk.tolist()
    #         # for i in range(0, len(chunk.tolist())
    #         for i in range(len(list)):
    #             col = list[i]
    #             if len(self.polygon) == 0:
    #                 yield col
    #             else:
    #                 for j in range(0,len(self.polygon)):
    #                     if self.check_point_inside(col[1], col[0], self.polygon[j]):
    #                         yield col
    #                         break
    def handle_event(self, event):
        if not self.input_stream.connected():
            return {'issue': 'NO DATA: Input is not connected.'}
        ev_type = event[0]
        time_credit = event[1]
        if ev_type == 'map_move':
            info = event[2]
            polygon = event[3]
            polyInfo = event[4]
            timeStart = event[5]
            timeEnd = event[6]
            # stream = SimpleStream('Mean result', self.compute)
            # stream.add_column('lat', float)
            # stream.add_column('lng', float)
            stream = self.filtered_stream(**polyInfo)
            # self.register_output(stream)
            # stream.length = 100;
            # create heatmap
            self.curr_heatmap = HeatMap(stream, polygon, timeStart, timeEnd, **info)
        # from now on, map_move or map_continue is the same thing
        # compute heatmap
        if ev_type == 'map_move' or ev_type == 'map_continue':
            self.curr_heatmap.compute(time_credit)
            # return compressed form
            compressed_hm = self.curr_heatmap.compressed_form()
            return { 'heatmap': compressed_hm }
        if ev_type == 'exportation':
            polygon = event[2]
            polyInfo = event[3]
            stream = self.filtered2_stream(**polyInfo)
            self.curr_exportation = Exportation(stream, polygon)
        if ev_type == 'exportation' or ev_type == 'exportation_continue':
            self.curr_exportation.compute(time_credit)
            compressed_ex = self.curr_exportation.compressed_form()
            # print(len(compressed_ex['data']['list']))
            # import pdb
            # pdb.set_trace()
            return { 'exportation': compressed_ex}   
        if ev_type == 'wordcloud':
            polygon = event[2]
            polyInfo = event[3]
            timeStart = event[4]
            timeEnd = event[5]
            stream = self.filtered2_stream(**polyInfo)
            self.curr_wordcloud = WordCloudInfo(stream, polygon, timeStart, timeEnd)
        if ev_type == 'wordcloud' or ev_type == 'wordcloud_continue':
            self.curr_wordcloud.compute(time_credit)
            compressed_wd = self.curr_wordcloud.compressed_form()
            return{'wordcloud': compressed_wd}
            