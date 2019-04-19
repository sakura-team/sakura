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

class lines:
    def __init__(self):

        self.vertices   = np.array([[0,0,0,0], [0,0,0,0]])
        self.sh         = sh.shader()
        self.sh.display = self.display

    def generate_buffers_and_attributes(self):
        self.vbo_vertices      = glGenBuffers(1)
        self.attr_vertices     = sh.new_attribute_index()

    def update_arrays(self):
        sh.bind(self.vbo_vertices, self.vertices, self.attr_vertices, 4, GL_FLOAT)

    def display(self):
        self.update_uniforms(self.sh)
        glDrawArrays(GL_LINES, 0, len(self.vertices))

    def update_unforms(self, sh):
        pass

    def create_shader(self, dir, glsl_version):
        return sh.create(   dir+'/lines.vert',
                            None,
                            dir+'/lines.frag',
                            [self.attr_vertices],
                            ['in_vertex'],
                            glsl_version)
