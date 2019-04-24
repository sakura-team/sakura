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

class trajectories:
    def __init__(self):

        self.vertices       = np.array([[0,0,0,0], [0,0,0,0], [0,0,0,0]])
        self.colors         = np.array([[0,0,0,1], [0,0,0,1], [0,0,0,1]])
        self.sh             = sh.shader()
        self.sh.display     = self.display
        self.display_color  = 'trajectories'   #other option is 'semantic'

        #Array used for point selection
        self.basic_colors_list = []
        for i in range(255*255*10):
            self.basic_colors_list.append(gm.id_to_color(i))
        self.basic_colors_list = np.array(self.basic_colors_list)


    def generate_buffers_and_attributes(self):
        self.vbo_vertices      = glGenBuffers(1)
        self.vbo_colors        = glGenBuffers(1)
        self.attr_vertices     = sh.new_attribute_index()
        self.attr_colors       = sh.new_attribute_index()

    def update_arrays(self, dcolor = 'none'):
        sh.bind(self.vbo_vertices, self.vertices, self.attr_vertices, 4, GL_FLOAT)

        tempd = self.display_color
        if dcolor != 'none':
            self.display_color = dcolor

        if self.display_color == 'trajectories':
            sh.bind(self.vbo_colors, self.colors, self.attr_colors, 4, GL_FLOAT)
        else:
            sh.bind(self.vbo_colors, self.sem_colors, self.attr_colors, 4, GL_FLOAT)

        self.display_color = tempd

    def display(self):
        self.update_uniforms(self.sh)
        glDrawArrays(GL_LINE_STRIP, 0, len(self.vertices))

    def update_unforms(self, sh):
        pass

    def create_shader(self, dir, glsl_version):
        return sh.create(   dir+'/trajects.vert',
                            None,
                            dir+'/trajects.frag',
                            [self.attr_vertices, self.attr_colors],
                            ['in_vertex', 'in_color'],
                            glsl_version)

    def geometry(self, data):
        self.vertices, self.colors, self.sem_colors = np.array(data.compute_geometry())
