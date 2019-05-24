#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#Michael ORTEGA - 26/Avril/2019

import numpy    as np

try:
    from OpenGL.GL      import *
    from OpenGL.GL      import shaders
except:
    print ('''ERROR in cube.py: PyOpenGL not installed properly. ** ''')

from .. import shader       as sh
from .. import mercator     as mrc


class contours:
    def __init__(self):
        self.vertices       = np.array([[0,0,0,0], [0,0,0,0], [0,0,0,0]])
        self.colors         = np.array([[0,0,0,1], [0,0,0,1], [0,0,0,1]])
        self.sh             = sh.shader()
        self.sh.display     = self.display

    def generate_buffers_and_attributes(self):
        self.vbo_vertices       = glGenBuffers(1)
        self.vbo_colors         = glGenBuffers(1)
        self.attr_vertices      = sh.new_attribute_index()
        self.attr_colors        = sh.new_attribute_index()

    def create_shader(self, dir, glsl_version):
        return sh.create(   dir+'/geo_contours.vert',
                            None,
                            dir+'/geo_contours.frag',
                            [self.attr_vertices, self.attr_colors],
                            ['in_vertex', 'in_color'],
                            glsl_version)

    def display(self):
        self.update_uniforms(self.sh)
        glDrawArrays(GL_LINE_STRIP, 0, len(self.vertices))

    def update_arrays(self):
        sh.bind(self.vbo_vertices, self.vertices, self.attr_vertices, 4, GL_FLOAT)
        sh.bind(self.vbo_colors, self.colors, self.attr_colors, 4, GL_FLOAT)

    def geometry(self, data, fsc):
        vertices   = []
        colors     = []

        for shape in fsc.shapes:
            m = mrc.mercator(*shape.points[0], 0)
            vertices.append([data.mins[0], *m])
            colors.append([0,0,0,0])

            for p in shape.points:
                m = mrc.mercator(*p, 0)
                vertices.append([data.mins[0], *m])
                colors.append([0,0,0,1])

            m = mrc.mercator(*shape.points[-1], 0)
            vertices.append([data.mins[0], *m])
            colors.append([0,0,0,0])

        self.vertices   = np.array(vertices)
        self.colors     = np.array(colors)

class areas:
    def __init__(self):
        self.vertices       = np.array([[0,0,0,0], [0,0,0,0], [0,0,0,0]])
        self.colors         = np.array([[0,0,0,1], [0,0,0,1], [0,0,0,1]])
        self.sh             = sh.shader()
        self.sh.display     = self.display

    def generate_buffers_and_attributes(self):
        self.vbo_vertices       = glGenBuffers(1)
        self.vbo_colors         = glGenBuffers(1)
        self.attr_vertices      = sh.new_attribute_index()
        self.attr_colors        = sh.new_attribute_index()

    def create_shader(self, dir, glsl_version):
        return sh.create(   dir+'/geo_areas.vert',
                            None,
                            dir+'/geo_areas.frag',
                            [self.attr_vertices, self.attr_colors],
                            ['in_vertex', 'in_color'],
                            glsl_version)

    def display(self):
        self.update_uniforms(self.sh)
        glEnable(GL_STENCIL_TEST)
        glDisable(GL_DEPTH_TEST)
        glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE)
        glStencilFunc(GL_ALWAYS, 0, -1)
        glStencilOp(GL_INVERT, GL_INVERT, GL_INVERT)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, len(self.vertices))
        glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
        glEnable(GL_DEPTH_TEST)
        glStencilFunc(GL_NOTEQUAL, 0, -1);
        glStencilOp(GL_REPLACE, GL_REPLACE, GL_REPLACE)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, len(self.vertices))
        glDisable(GL_STENCIL_TEST)


    def update_arrays(self):
        sh.bind(self.vbo_vertices, self.vertices, self.attr_vertices, 4, GL_FLOAT)
        sh.bind(self.vbo_colors, self.colors, self.attr_colors, 4, GL_FLOAT)

    def geometry(self, data, fsc):
        vertices   = []
        colors     = []

        for shape in fsc.shapes:
            m = mrc.mercator(*shape.triangles[0], 0)
            vertices.append([data.mins[0], *m])
            colors.append([0,0,0,0])

            for p in shape.triangles:
                m = mrc.mercator(*p, 0)
                vertices.append([data.mins[0], *m])
                colors.append([1,1,1,.7])

            m = mrc.mercator(*shape.triangles[-1], 0)
            vertices.append([data.mins[0], *m])
            colors.append([0,0,0,0])

        self.vertices   = np.array(vertices)
        self.colors     = np.array(colors)
