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
        lng_column, lat_column = \
            self.lng_column_param.value, self.lat_column_param.value
        # filter input stream as much as possible:
        # - select useful columns only
        # - restrict to visible area
        stream = self.input_stream
        stream = stream.select_columns(lng_column, lat_column)
        # import pdb
        # pdb.set_trace()
        stream = stream.filter(lng_column >= westlng)
        stream = stream.filter(lng_column <= eastlng)
        stream = stream.filter(lat_column >= southlat)
        stream = stream.filter(lat_column <= northlat)
        if disable :
            stream = stream.filter(lat_column > northlat)
        return stream
    def filtered2_stream(self, westlng, eastlng, southlat, northlat, disable, **args):
        # get columns selected in combo parameters
        lng_column, lat_column, time_column, text_column = \
            self.lng_column_param.value, self.lat_column_param.value, self.time_column_param.value, self.text_column_param.value
        # filter input stream as much as possible:
        # - select useful columns only
        # - restrict to visible area
        stream = self.input_stream
        stream = stream.select_columns(lng_column, lat_column, time_column, text_column)
        stream = stream.filter(lng_column >= westlng)
        stream = stream.filter(lng_column <= eastlng)
        stream = stream.filter(lat_column >= southlat)
        stream = stream.filter(lat_column <= northlat)
        if disable :
            stream = stream.filter(lat_column > northlat)
        return stream
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
            listWords = event[7]
            # stream = SimpleStream('Mean result', self.compute)
            # stream.add_column('lat', float)
            # stream.add_column('lng', float)
            if len(polygon)==0:
                stream = self.filtered_stream(**polyInfo)
            else:
                stream = self.filtered2_stream(**polyInfo)
            # self.register_output(stream)
            # stream.length = 100;
            # create heatmap
            self.curr_heatmap = HeatMap(stream, polygon, timeStart, timeEnd, listWords, **info)
            self.curr_heatmap.compute(time_credit)
            compressed_hm = self.curr_heatmap.compressed_form()
            return { 'heatmap': compressed_hm }
        # from now on, map_move or map_continue is the same thing
        # compute heatmap
        elif ev_type == 'map_continue':
            self.curr_heatmap.compute(time_credit)
            # return compressed form
            compressed_hm = self.curr_heatmap.compressed_form()
            return { 'heatmap': compressed_hm }
        elif ev_type == 'exportation':
            polyInfo = event[2]
            polygon = event[3]
            timeStart = event[4]
            timeEnd = event[5]
            listWords = event[6]
            stream = self.filtered2_stream(**polyInfo)
            self.curr_exportation = Exportation(stream, polygon, timeStart, timeEnd, listWords)
            self.curr_exportation.compute(time_credit)
            compressed_ex = self.curr_exportation.compressed_form()
            return { 'exportation': compressed_ex}   
        elif ev_type == 'exportation_continue':
            self.curr_exportation.compute(time_credit)
            compressed_ex = self.curr_exportation.compressed_form()
            # import pdb
            # pdb.set_trace()
            return { 'exportation': compressed_ex}   
        elif ev_type == 'wordcloud':
            polyInfo = event[2]
            polygon = event[3]
            timeStart = event[4]
            timeEnd = event[5]
            words = event[6]
            stream = self.filtered2_stream(**polyInfo)
            self.curr_wordcloud = WordCloudInfo(stream, polygon, timeStart, timeEnd, words)
            self.curr_wordcloud.compute(time_credit)
            compressed_wd = self.curr_wordcloud.compressed_form()
            return{'wordcloud': compressed_wd}
        elif ev_type == 'wordcloud_continue':
            self.curr_wordcloud.compute(time_credit)
            compressed_wd = self.curr_wordcloud.compressed_form()
            return{'wordcloud': compressed_wd}
        elif ev_type == 'otherwise':
            return{'otherwise': 'nodata'}
            