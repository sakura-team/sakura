#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#Michael ORTEGA for PIMLIG/LIG/CNRS- 10/12/2018

#################################
## GLOBAL LIBS
import sys, math, time
import numpy as np

try:
    from OpenGL.GL      import *
    from OpenGL.GLU     import *
    from OpenGL.GL      import shaders
except:
    print ('''ERROR: PyOpenGL not installed properly. ** ''')

from .libs import shader             as sh
from .libs import projector          as pr

def wire_cube(pos, edge):
    p = np.array(pos)
    e = edge/2.
    return [    [pos + np.array([-e, -e, e])],
                [pos + np.array([e, -e, e])],
                [pos + np.array([e, -e, e])],
                [pos + np.array([e, e, e])],
                [pos + np.array([e, e, e])],
                [pos + np.array([-e, e, e])],
                [pos + np.array([-e, e, e])],
                [pos + np.array([-e, -e, e])],

                [pos + np.array([-e, -e, -e])],
                [pos + np.array([e, -e, -e])],
                [pos + np.array([e, -e, -e])],
                [pos + np.array([e, e, -e])],
                [pos + np.array([e, e, -e])],
                [pos + np.array([-e, e, -e])],
                [pos + np.array([-e, e, -e])],
                [pos + np.array([-e, -e, -e])],

                [pos + np.array([-e, -e, -e])],
                [pos + np.array([-e, -e, e])],
                [pos + np.array([e, -e, -e])],
                [pos + np.array([e, -e, e])],
                [pos + np.array([e, e, -e])],
                [pos + np.array([e, e, e])],
                [pos + np.array([-e, e, -e])],
                [pos + np.array([-e, e, e])]    ]


class HelloCube:
    def __init__(self, op_dir):
        # import local libs
        self.hellocube_dir = op_dir / 'hellocube'
        # display attributes
        self.width = 100
        self.height = 100
        self.cube_shader = sh.shader()
        self.projo = pr.projector(position = [0, 0, 2])

        self.fps_limitation = 60    #Hz
        self.last_time      = time.time()
        self.label = "3D cube"

    def init(self):
        self.mouse = [ 0, 0 ]
        self.imode = 'none'
        glEnable(GL_MULTISAMPLE)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
        self.init_shader()

    def init_shader(self):
        glsl_version = glGetString(GL_SHADING_LANGUAGE_VERSION).decode("utf-8")
        glsl_version = glsl_version.replace('.', '').split()[0]

        ##########################
        # general vertex array object
        print('\n\tGenerating vao...', end='')
        sys.stdout.flush()
        try:
            vao = glGenVertexArrays(1)
            glBindVertexArray(vao)
            print('\tOk')
            sys.stdout.flush()
        except ValueError:
            print()
            print()
            print(ValueError)
            print()
            sys.exit()

        ##########################
        # simple cube
        self.cube_vbo           = glGenBuffers(1)
        self.cube_vertices      = np.array(wire_cube([0,0,0], 1))
        self.cube_shader.attr_vertices = sh.new_attribute_index()

        ## CALLBACKS -------
        #update arrays callback
        def _update_arrays():
            sh.bind(self.cube_vbo, self.cube_vertices, self.cube_shader.attr_vertices, 3, GL_FLOAT)
        self.cube_shader.update_arrays = _update_arrays

        # display callback
        def cube_display():
            self.cube_shader.update_projections(self.projo.projection(), self.projo.modelview())
            glDrawArrays(GL_LINES, 0, len(self.cube_vertices))
        self.cube_shader.display = cube_display
        ## CALLBACKS -------

        #first array update
        self.cube_shader.update_arrays()

        #Loading shader files
        print('\tCube shader...', end='')
        self.cube_shader.sh = sh.create(str(self.hellocube_dir / 'shaders/cube.vert'), None,
                                             str(self.hellocube_dir / 'shaders/cube.frag'), [self.cube_shader.attr_vertices], ['in_vertex'], glsl_version)
        if not self.cube_shader.sh:
            exit(1)
        print('\t\tOk')
        sys.stdout.flush()

    def display(self):
        glClearColor(.31,.63,1.0,1.0)
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)
        sh.display_list([self.cube_shader])

    def on_mouse_click(self, button, state, x, y):
        self.mouse = [x, y]
        LEFT_BUTTON = 0
        MIDDLE_BUTTON = 1
        RIGHT_BUTTON = 2
        DOWN = 0
        UP = 1
        if button == LEFT_BUTTON and state == DOWN:
            self.imode = 'rotation'
        elif button == LEFT_BUTTON and state == UP:
            self.imode = 'none'

    def on_mouse_motion(self, x, y):
        if self.imode == 'rotation':
            dx, dy = x - self.mouse[0], y - self.mouse[1]
            self.projo.rotate_h(-dx/self.width*math.pi)
            self.projo.rotate_v(-dy/self.height*math.pi)
        self.mouse = [x, y]

    def on_key_press(self, key, x, y):
        if key == b'\x1b':
            sys.exit()
        elif key == b't':
            print('test', x, y)

    def on_resize(self, w, h):
        print('resize ' + str((w, h)))
        glViewport(0,  0,  w,  h);
        self.projo.change_ratio(w/float(h))
        self.width, self.height = w, h
