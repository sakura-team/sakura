#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#Michael ORTEGA - 07/April/2017

import time, datetime
import  numpy as np
import copy
from . import geomaths as gm
from . import mercator as mrc


class trajectory:
    def __init__(self, id=0):
        self.points                     = []            # points that define a trajectory: (long, elevation, -lat, time)
        self.color                      = np.array([])  # color
        self.zones                      = np.array([])  # a zone is defined by [gps position, radius, starting date, ending date]
        self.display_indice             = 0             # indice of begining of the trajectory in the whole array of data display

class data:
    def  __init__(self):
        self.init()

    def init(self):
        self.selected       = []
        self.trajects       = []
        self.trajects_names = []
        self.trajects_ids   = []                # we identify the trajectories by a factice color facilitating opengl selection
        self.trajects_ind   = []                # indices of each trajectory in the whole array of geometric data
        self.maxs           = [1, 1, 1, 1]      #[time, lon, lat, ele]
        self.mins           = [0, 0, 0, 0]      #[time, lon, lat, ele]

    def clean(self):
        self.init()

    def add(self, chunk):
        ''' adding new data: maybe new trajectories, maybe a new piece of existing trajectory'''
        nd = []
        first_time = False
        for c in chunk:
            if len(self.trajects_names) == 0:
                first_time = True
                self.trajects_names = [c[0]]
                self.trajects = np.append(self.trajects, trajectory(id=len(self.trajects)-1))
                self.trajects[-1].color = np.array([*gm.random_color(), 1])
                self.trajects_ids = [gm.color_to_id(copy.copy(self.trajects[-1].color))]

            elif c[0] not in self.trajects_names:
                self.trajects_names.append(c[0])
                self.trajects = np.append(self.trajects, trajectory(id=len(self.trajects)-1))

                color = [*gm.random_color(), 1]
                id = gm.color_to_id(np.array(color))
                while id in self.trajects_ids:
                    color = [*gm.random_color(), 1]
                    id = gm.color_to_id(np.array(color))

                self.trajects[-1].color = color
                self.trajects_ids.append(id)

            ind = self.trajects_names.index(c[0])
            m = mrc.mercator(c[2], c[3], c[4])
            self.trajects[ind].points.append([c[1], *m])
            nd.append([c[1], *m])

        if not first_time:
            nd.append([*self.maxs])
            nd.append([*self.mins])
        self.make_meta(nd)

    def make_meta(self, new_data=[]):
        '''making meta data from current data: min and max times, size, ...'''
        maxs = []
        mins = []
        if len(new_data) == 0:
            for t in self.trajects:
                maxs.append(np.amax(t.points, axis = 0))
                mins.append(np.amin(t.points, axis = 0))
            self.maxs = np.amax(maxs, axis = 0)
            self.mins = np.amin(mins, axis = 0)
        else:
            self.maxs = np.amax(new_data, axis = 0)
            self.mins = np.amin(new_data, axis = 0)

    def print_meta(self):
        print('\ndata info')
        print('\tNb trajectories:\t'+ str(len(self.trajects)))
        tpt = 0
        for t in self.trajects:
            tpt += len(t.points)
        print('\t\tTotal points:\t'+ str(tpt))
        print('\ttime duration:\t'+ str(datetime.timedelta(seconds=(self.maxs[0] - self.mins[0]))))
        print('\tCube size:\t\t'+str(self.maxs[1:] - self.mins[1:] )+'\n')

    def compute_geometry(self):
        vertices    = []
        colors      = []
        for t in self.trajects:
            t.display_indice =  len(vertices)
            vertices.append(t.points[0])
            colors.append([0,0,0,0])
            for p in t.points:
                vertices.append(p)
                colors.append(t.color)
            vertices.append(t.points[-1])
            colors.append([0,0,0,0])
        return np.array(vertices), np.array(colors)
