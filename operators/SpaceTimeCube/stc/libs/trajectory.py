#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#Michael ORTEGA - 07/April/2017

import datetime
import  numpy as np
from . import geomaths as gm
from . import mercator as merc

class trajectory:
    def __init__(self, id=0):
        self.id                         = id            # we identify the trajectories by a factice color facilitating opengl selection
        self.points                     = []            # points that define a trajectory: (long, elevation, -lat, time)
        self.color                      = np.array([])  # color
        self.zones                      = np.array([])  # a zone is defined by [gps position, radius, starting date, ending date]

class data:
    def  __init__(self):
        self.init()

    def init(self):
        self.selected       = []
        self.trajects       = []
        self.trajects_ids   = []
        self.trajects_ind   = []                                # indices of each trajectory in the whole array of geometric data
        self.mins           = [-1, -1, -1]
        self.maxs           = [1, 1, 1]
        self.mid            = [0, 0, 0]
        self.time_min       = 0
        self.time_max       = 0

    def add(self, chunk):
        ''' adding new data: maybe new trajectories, maybe a new piece of existing trajectory'''
        for c in chunk:
            if len(self.trajects_ids) == 0:
                self.trajects_ids = [c[0]]
                self.trajects = np.append(self.trajects, trajectory(id=len(self.trajects)-1))
            elif c[0] not in self.trajects_ids:
                self.trajects_ids.append(c[0])
                self.trajects = np.append(self.trajects, trajectory(id=len(self.trajects)-1))

            ind = self.trajects_ids.index(c[0])
            self.trajects[ind].points.append([c[1], c[2], c[3], c[4]])

    def make_meta(self):
        '''making meta data from current data: min and max times, size, ...'''
        maxs = []
        mins = []
        for t in self.trajects:
            maxs.append(np.amax(t.points, axis = 0))
            mins.append(np.amin(t.points, axis = 0))
        maxs = np.amax(maxs, axis = 0)
        mins = np.amax(mins, axis = 0)
        self.size_max = maxs[1:]
        self.size_min = mins[1:]
        self.time_max = maxs[0]
        self.time_min = mins[0]

    def print_meta(self):
        print('\ndata info')
        print('\tNb trajectories:\t'+ str(len(self.trajects)))
        print('\ttime duration:\t'+ str(datetime.timedelta(seconds=(self.time_max - self.time_min))))
        print('\tCube size:\t\t'+str(self.size_max - self.size_min )+'\n')

    def compute_geometry(self):
        pass
