#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#Started by Michael ORTEGA - 20/Sept/2018
import numpy    as      np

from .. import shader        as sh
from .. import geomaths      as gm

try:
    from OpenGL.GL      import *
    from OpenGL.GL      import shaders
except:
    print ('''ERROR in cube.py: PyOpenGL not installed properly. ** ''')

def wire_cube(mins, maxs):
    size = np.fabs(maxs - mins)
    return np.array([
                #verticals
                mins + np.array([size[0], 0, size[0]]),
                mins + np.array([size[0], size[0], size[0]]),
                mins + np.array([size[0], 0, 0]),
                mins + np.array([size[0], size[0], 0]),
                mins,
                mins + np.array([0, size[0], 0]),
                mins + np.array([0, 0, size[0]]),
                mins + np.array([0, size[0], size[0]]),

                #ground
                mins + np.array([size[0], 0, size[0]]),
                mins + np.array([size[0], 0, 0]),
                mins + np.array([size[0], 0, 0]),
                mins,
                mins,
                mins + np.array([0, 0, size[0]]),
                mins + np.array([0, 0, size[0]]),
                mins + np.array([size[0], 0, size[0]]),

                #top
                mins + np.array([size[0], size[0], size[0]]),
                mins + np.array([size[0], size[0], 0]),
                mins + np.array([size[0], size[0], 0]),
                mins + np.array([0, size[0], 0]),
                mins + np.array([0, size[0], 0]),
                mins + np.array([0, size[0], size[0]]),
                mins + np.array([0, size[0], size[0]]),
                mins + np.array([size[0], size[0], size[0]]),
                ])

class cube:
    def __init__(self,  mins=np.array([-.5,-.5,-.5]),
                        maxs=np.array([.5,.5,.5])):

        self.height                 = maxs[1] - mins[1]
        self.proj_corners_bottom    = []
        self.proj_corners_up        = []

        self.sh            = sh.shader()
        self.vertices      = wire_cube(mins, maxs)
        self.colors        = np.full((len(self.vertices)*3), .5)
        self.colors        = self.colors.reshape(int(len(self.vertices)), 3)

        self.sh.display = self.display

        self.reset()

    def reset(self):
        self.current_edge   = -1

    def set_height(self, value):
        if value > 1.0:     self.height = 1.0
        elif value <= 0.0:  self.height = 0.00001
        else:               self.height = value

    def generate_buffers_and_attributes(self):
        self.vbo_vertices      = glGenBuffers(1)
        self.vbo_colors        = glGenBuffers(1)
        self.attr_vertices     = sh.new_attribute_index()
        self.attr_colors       = sh.new_attribute_index()

    def update_arrays(self):
        sh.bind(self.vbo_vertices, self.vertices, self.attr_vertices, 3, GL_FLOAT)
        sh.bind(self.vbo_colors, self.colors, self.attr_colors, 3, GL_FLOAT)

    def display(self):
        self.update_uniforms(self.sh)
        glDrawArrays(GL_LINES, 0, len(self.vertices))

    def update_unforms(self, sh):
        pass

    def create_shader(self, dir, glsl_version):
        return sh.create(   dir+'/cube.vert',
                            None,
                            dir+'/cube.frag',
                            [self.attr_vertices, self.attr_colors],
                            ['in_vertex', 'in_color'],
                            glsl_version)

    def closest_edge(self, threshold, m):
        '''from cube corner projections and mouse position,
        we give the closest cube indice'''

        #m = [self.mouse[0], self.height - self.mouse[1]]

        #vertical edges only for now
        dist = float('inf')
        index = -1
        for i in range(len(self.proj_corners_bottom)):
            a = self.proj_corners_bottom[i]
            b = self.proj_corners_up[i]
            d = gm.distance_2D(gm.proj_pt_on_line(m, a, b), m)
            if d < dist:
                index = i
                dist = d

        if dist < threshold:
            return index
        return -1

    def project_corner(self, p, traj_size, projo, win_size):
        if traj_size[0] > traj_size[1]:
            p[2] *= traj_size[1]/traj_size[0]
        else:
            p[0] *= traj_size[0]/traj_size[1]
        p[1] = p[1]*self.height - self.height/2;
        pp = projo.project_on_screen([p[0], p[1], p[2], 1.0] )
        return [ (pp[0]+1)/2*win_size[0], (pp[1]+1)/2*win_size[1]]

    def compute_proj_corners(self,size, m, projo, win):
        self.proj_corners_bottom = [
                self.project_corner([.5, 0.,.5], size, projo, win),
                self.project_corner([.5, 0.,-.5], size, projo, win),
                self.project_corner([-.5, 0.,-.5], size, projo, win),
                self.project_corner([-.5, 0.,.5], size, projo, win)
                ]
        self.proj_corners_up = [
                self.project_corner([.5, 1.,.5], size, projo, win),
                self.project_corner([.5, 1.,-.5], size, projo, win),
                self.project_corner([-.5, 1.,-.5], size, projo, win),
                self.project_corner([-.5, 1.,.5], size, projo, win)
                ]

        #Are we on an edge ?
        index = -1
        if len(self.proj_corners_bottom):
            index = self.closest_edge(5,m)

        if index != -1:
            self.colors[index*2] = [1,1,1]
            self.colors[index*2+1] = [1,1,1]
        if index == -1 or index != self.current_edge:
            self.colors[self.current_edge*2] = [.5,.5,.5]
            self.colors[self.current_edge*2+1] = [.5,.5,.5]
        self.current_edge = index

    def crop_mode(self, m):
        a = self.proj_corners_bottom[self.current_edge]
        b = self.proj_corners_up[self.current_edge]
        dist_a = gm.distance_2D(m, a)
        dist_b = gm.distance_2D(m, b)
        if dist_a < dist_b:
            return 'crop_down'
        return 'crop_up'

    def scale(self, delta):
        a = self.proj_corners_bottom[self.current_edge]
        b = self.proj_corners_up[self.current_edge]

        dist = gm.distance_2D(a, b)
        amount  = 0
        dot     = 0
        if dist > 0:
            amount  = gm.norm(delta)/gm.distance_2D(a, b)
            dot     = gm.dot(   gm.normalize(gm.vector(a, b)),
                                gm.normalize(delta))
        if dot <= -0.5:
            self.set_height(self.height + amount*self.height)
        elif dot >= 0.5:
            self.set_height(self.height - amount*self.height)
