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
        self.semantics                  = []            # each point can have a semantic, then a color could be used for
        self.sem_colors                 = np.array([])

class data:
    def  __init__(self):
        self.init()

    def init(self):
        self.selected       = []
        self.displayed      = []
        self.trajects       = []
        self.trajects_names = []
        self.trajects_ids   = []                # we identify the trajectories by a factice color facilitating opengl selection
        self.maxs           = [1, 1, 1, 1]      #[time, lon, lat, ele]
        self.mins           = [0, 0, 0, 0]      #[time, lon, lat, ele]
        self.semantics      = []
        self.sem_colors     = []
        self.colors_file    = None
        self.hl_semantic    = 0                 # the current semantic that gives the trakectory its color
        self.semantic_names = []

    def clean(self):
        self.init()

    def add(self, chunk):
        ''' adding new data: maybe new trajectories, maybe a new piece of existing trajectory'''
        for c in chunk:
            if len(self.trajects_names) == 0:
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
            m = mrc.mercator(c['longitude'], c['latitude'], c['elevation'])
            self.trajects[ind].points.append([c[1], *m])

            self.semantic_names = []
            if len(c) > 5:  #We have a semantic
                arr = []
                for n in c.dtype.names:
                    if not n in ['trajectory', 'date', 'longitude', 'latitude', 'elevation']:
                        arr.append(c[n])
                        self.semantic_names.append(n)
                self.trajects[ind].semantics.append(arr)

        self.displayed = list(range(len(self.trajects)))
        self.make_meta()

    def make_meta(self):
        '''making meta data from current data: min and max times, size, ...'''

        indices = []
        for i in range(len(self.trajects)):
            for p in self.trajects[i].points:
                if p[1] == 0.0:
                    indices.append(i)
                    break

        for i in reversed(indices):
            self.trajects       = np.delete(self.trajects, i).tolist()
            self.trajects_names = np.delete(self.trajects_names, i).tolist()
            self.trajects_ids   = np.delete(self.trajects_ids, i).tolist()

        maxs = []
        mins = []
        sems = []
        for t, i in zip(self.trajects, range(len(self.trajects))):
            if i in self.displayed:
                maxs.append(np.amax(t.points, axis = 0))
                mins.append(np.amin(t.points, axis = 0))
            u = np.unique(t.semantics)
            for n in u:
                sems.append(n)
        if len(maxs) > 0:
            self.maxs = np.amax(maxs, axis = 0)
            self.mins = np.amin(mins, axis = 0)

        self.semantics = list(np.unique(sems))
        self.sem_colors = []
        if not self.colors_file:
            for s in self.semantics:
                self.sem_colors.append([*gm.random_color(), 1])
        else:
            for s in self.semantics:
                self.sem_colors.append([*gm.random_color(), 1])

            fcolors = open(self.colors_file, 'r').readlines()
            colors = []
            for f in fcolors[1:]:
                c = f.split(',')
                h = c[-1].rstrip().lstrip('#')
                c[-1] = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

                if c[0] in self.semantics:
                    ind = self.semantics.index(c[0])
                    self.sem_colors[ind] = [c[1][0]/255, c[1][1]/255, c[1][2]/255, 1.0]

        self.update_sem_colors()

    def update_sem_colors(self, sem_index = -1):
        if sem_index >= 0 and sem_index < len(self.trajects[0].semantics):
            self.hl_semantic = sem_index

        for t in self.trajects:
            t.sem_colors = []
            for s in t.semantics:
                ind = self.semantics.index(s[self.hl_semantic])
                t.sem_colors.append(self.sem_colors[ind])

    def get_semantic_names(self):
        return self.semantic_names

    def print_meta(self):
        print('\ndata info')
        print('\tNb trajectories:\t'+ str(len(self.trajects)))
        tpt = 0
        for t in self.trajects:
            tpt += len(t.points)
        print('\t\tTotal points:\t'+ str(tpt))
        print('\ttime duration:\t'+ str(datetime.timedelta(seconds=(self.maxs[0] - self.mins[0]))))
        print('\tCube size:\t\t'+str(self.maxs[1:] - self.mins[1:] )+'\n')

    def compute_geometry(self, semantic = False):

        vertices    = []
        colors      = []
        sem_colors  = []
        for t, i in zip(self.trajects, range(len(self.trajects))):
            if i in self.displayed:
                t.display_indice =  len(vertices)
                vertices.append(t.points[0])
                colors.append([0,0,0,0])
                if len(t.sem_colors) > 0:
                    sem_colors.append([0,0,0,0])
                    for p, i in zip(t.points, range(len(t.points))):
                        vertices.append(p)
                        colors.append(t.color)
                        sem_colors.append(t.sem_colors[i])
                    sem_colors.append([0,0,0,0])
                else:
                    for p in t.points:
                        vertices.append(p)
                        colors.append(t.color)
                vertices.append(t.points[-1])
                colors.append([0,0,0,0])

        return np.array(vertices), np.array(colors), np.array(sem_colors)

    def compute_line_vertices(self, pt):
        return np.array([   pt, [self.mins[0],*pt[1:]],
                            [pt[0], *self.mins[1:]],  [pt[0], self.maxs[1], *self.mins[2:]],
                            [pt[0], *self.mins[1:]],  [pt[0], self.mins[1], self.maxs[2], self.mins[3]],
                            [pt[0], *self.maxs[1:]],  [pt[0], self.mins[1], *self.maxs[2:]],
                            [pt[0], *self.maxs[1:]],  [pt[0], self.maxs[1], *self.mins[2:]]
                            ])

    def compute_quad_vertices(self, pt):
        return np.array([   [pt[0], *self.mins[1:]],
                            [pt[0], self.maxs[1], *self.mins[2:]],
                            [pt[0], self.mins[1], self.maxs[2], self.mins[3]],

                            [pt[0], self.mins[1], self.maxs[2], self.mins[3]],
                            [pt[0], self.maxs[1], *self.mins[2:]],
                            [pt[0], *self.maxs[1:]]
                            ])
