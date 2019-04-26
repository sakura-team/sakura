#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#Michael ORTEGA - 26/Avril/2019

import geojson  as gj
import numpy    as np

try:
    from OpenGL.GL      import *
    from OpenGL.GL      import shaders
except:
    print ('''ERROR in cube.py: PyOpenGL not installed properly. ** ''')

from .. import shader       as sh
from .. import mercator     as mrc


class floor_shape:
    def __init__(self, name, points):
        self.name   = name
        self.points = points


class floor_shapes:
    def __init__(self):
        self.shapes         = []
        self.vertices       = np.array([[0,0,0,0], [0,0,0,0], [0,0,0,0]])
        self.colors         = np.array([[0,0,0,1], [0,0,0,1], [0,0,0,1]])
        self.sh             = sh.shader()
        self.sh.display     = self.display
        self.displayed      = True

    def read_shapes(self, fname):
        if fname:
            geoj = gj.load(open(fname, 'r'))

            for f in geoj['features']:
                n = f['properties']['name']
                c = f['geometry']['coordinates']
                out = []
                while len(c) > 0:
                    elem = c.pop()
                    if isinstance(elem, list):
                        for e in elem:
                            c.append(e)
                    else:
                        out.append(elem)

                out.reverse()
                out = np.reshape(np.array(out), (-1, 2))
                self.shapes.append( floor_shape(n, out))


    def generate_buffers_and_attributes(self):
        self.vbo_vertices       = glGenBuffers(1)
        self.vbo_colors         = glGenBuffers(1)
        self.attr_vertices      = sh.new_attribute_index()
        self.attr_colors        = sh.new_attribute_index()

    def create_shader(self, dir, glsl_version):
        return sh.create(   dir+'/floor_shapes.vert',
                            None,
                            dir+'/floor_shapes.frag',
                            [self.attr_vertices, self.attr_colors],
                            ['in_vertex', 'in_color'],
                            glsl_version)

    def display(self):
        self.update_uniforms(self.sh)
        glDrawArrays(GL_LINE_STRIP, 0, len(self.vertices))

    def update_arrays(self):
        sh.bind(self.vbo_vertices, self.vertices, self.attr_vertices, 4, GL_FLOAT)
        sh.bind(self.vbo_colors, self.colors, self.attr_colors, 4, GL_FLOAT)

    def geometry(self, data):
        vertices   = []
        colors     = []
        for shape in self.shapes:
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
