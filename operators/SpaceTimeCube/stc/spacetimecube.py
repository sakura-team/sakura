#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#Michael ORTEGA for PIMLIG/LIG/CNRS- 10/12/2018

import sys, math, time, inspect, datetime
import numpy as np
from pathlib import Path

try:
    from OpenGL.GL      import *
    from OpenGL.GLU     import *
    from OpenGL.GL      import shaders
except:
    print ('''ERROR: PyOpenGL not installed properly. ** ''')

from .libs import shader        as sh
from .libs import projector     as pr
from .libs import trajectory    as tr

def wire_cube(pos, edge):
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


class SpaceTimeCube:
    def __init__(self):
        # import local libs
        spacetimecube_py_path = Path(inspect.getabsfile(self.__class__))
        self.spacetimecube_dir = spacetimecube_py_path.parent
        # display attributes
        self.width = 100
        self.height = 100

        self.projo = pr.projector(position = [0, 0, 2])
        self.projo.wiggle = True
        self.projo.rotate_v(-math.pi/15)

        self.fps_limitation = 60    #Hz
        self.last_time      = time.time()
        self.label = "3D cube"

        #Shaders
        self.sh_cube    = sh.shader()
        self.sh_shadows = sh.shader()

        #Trajectory data
        self.data = tr.data()

        #Global display data
        self.cube_vertices      = np.array(wire_cube([0,0,0], 1))
        self.trajects_vertices  = np.array([[0,-1000,0,0], [0,1000,0,0]]) #[time, lon, lat, ele]

    def init(self):
        self.mouse = [ 0, 0 ]
        self.imode = 'none'
        glEnable(GL_MULTISAMPLE)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
        print('\n-------------------------')
        print('Inits')
        self.init_shaders()
        print('-------------------------')

    def init_shaders(self):

        glsl_version = glGetString(GL_SHADING_LANGUAGE_VERSION).decode("utf-8").replace('.', '')

        ##########################
        # general vertex array object
        print('\t\33[1;32mGenerating vao...\33[m', end='')
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
        # VBOS & attributes
        self.vbo_cube                = glGenBuffers(1)
        self.vbo_trajects            = glGenBuffers(1)
        self.attr_cube_vertices      = sh.new_attribute_index()
        self.attr_trajects_vertices  = sh.new_attribute_index()

        ##########################
        # Shaders
        #-----------------------------------------------
        # Cube
        ## CALLBACKS -------
        def _update_cube_arrays():
            sh.bind(self.vbo_cube, self.cube_vertices, self.attr_cube_vertices, 3, GL_FLOAT)
        self.sh_cube.update_arrays = _update_cube_arrays

        def cube_display():
            self.sh_cube.update_projections(self.projo.projection(), self.projo.modelview())
            glDrawArrays(GL_LINES, 0, len(self.cube_vertices))
        self.sh_cube.display = cube_display
        ## CALLBACKS -------
        self.sh_cube.update_arrays()

        # Loading shader files
        print('\t\33[1;32mCube shader...\33[m', end='')
        sys.stdout.flush()
        self.sh_cube.sh = sh.create(str(self.spacetimecube_dir / 'shaders/cube.vert'),
                                    None,
                                    str(self.spacetimecube_dir / 'shaders/cube.frag'),
                                    [self.attr_cube_vertices], ['in_vertex'],
                                    glsl_version)
        if not self.sh_cube.sh: exit(1)
        print('\t\tOk')
        sys.stdout.flush()
        #-----------------------------------------------

        #-----------------------------------------------
        # Shadows
        ## CALLBACKS -------
        def _update_trajects_arrays():
            sh.bind(self.vbo_trajects, self.trajects_vertices, self.attr_trajects_vertices, 4, GL_FLOAT)
        self.sh_shadows.update_arrays = _update_trajects_arrays

        def trajects_display():
            self.sh_shadows.update_projections(self.projo.projection(), self.projo.modelview())
            glDrawArrays(GL_LINE_STRIP, 0, len(self.trajects_vertices))
        self.sh_shadows.display = trajects_display
        ## CALLBACKS -------
        self.sh_shadows.update_arrays()

        # Loading shader files
        print('\t\33[1;32mShadows shader...\33[m', end='')
        sys.stdout.flush()
        self.sh_shadows.sh = sh.create( str(self.spacetimecube_dir / 'shaders/shadows.vert'),
                                        None,
                                        str(self.spacetimecube_dir / 'shaders/shadows.frag'),
                                        [self.attr_trajects_vertices],
                                        ['in_vertex'],
                                        glsl_version)

        if not self.sh_shadows.sh: exit(1)
        print('\tOk')
        sys.stdout.flush()
        #-----------------------------------------------

    def load_data(self, chunk=[], file=''):
        if len(chunk) >0:
            self.data.add(chunk)
            print(chunk[0])
        elif file != '':
            print('\t\33[1;32mReading data...\33[m', end='')
            sys.stdout.flush()
            big_chunk = np.recfromcsv(file, delimiter=',', encoding='utf-8')
            if type(big_chunk[0][1]) != int:
                for b in big_chunk:
                    b[1] = int(datetime.datetime.strptime(b[1], '%Y-%m-%d %H:%M:%S').strftime("%s"))
                big_chunk = big_chunk.astype([  ('trajectory', big_chunk.dtype[0]),
                                                ('date', big_chunk.dtype[2]),
                                                ('longitude', big_chunk.dtype[2]),
                                                ('latitude', big_chunk.dtype[3]),
                                                ('elevation', big_chunk.dtype[4])])
            self.data.add(big_chunk[ : int(len(big_chunk)/2)])
            self.data.add(big_chunk[int(len(big_chunk)/2) : ])
        print('\t\tOk')
        sys.stdout.flush()

        self.data.print_meta()
        self.trajects_vertices = np.array(self.data.compute_geometry())
        print(self.trajects_vertices[0])
        self.sh_shadows.update_arrays()
        self.resize_cube()

    def resize_cube(self):
        pass

    def display(self):
        glClearColor(.31,.63,1.0,1.0)
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)
        sh.display_list([self.sh_cube, self.sh_shadows])

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
        elif key == b'w':
            self.projo.wiggle = not self.projo.wiggle

    def on_resize(self, w, h):
        print('resize ' + str((w, h)))
        glViewport(0,  0,  w,  h);
        self.projo.change_ratio(w/float(h))
        self.width, self.height = w, h

    def animation(self):
        if self.projo.wiggle:
            self.projo.wiggle_next()
