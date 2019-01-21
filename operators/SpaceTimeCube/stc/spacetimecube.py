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

def wire_cube(mins, maxs):
    size = np.fabs(maxs - mins)
    return np.array(
            [   mins,
                mins + np.array([size[0], 0, 0]),
                mins + np.array([size[0], 0, 0]),
                mins + np.array([size[0], size[0], 0]),
                mins + np.array([size[0], size[0], 0]),
                mins + np.array([0, size[0], 0]),
                mins + np.array([0, size[0], 0]),
                mins,

                maxs,
                maxs - np.array([size[0], 0, 0]),
                maxs - np.array([size[0], 0, 0]),
                maxs - np.array([size[0], size[0], 0]),
                maxs - np.array([size[0], size[0], 0]),
                maxs - np.array([0, size[0], 0]),
                maxs - np.array([0, size[0], 0]),
                maxs,

                mins,
                mins + np.array([0, 0, size[0]]),
                mins + np.array([0, size[0], 0]),
                mins + np.array([0, size[0], size[0]]),

                maxs,
                maxs - np.array([0, 0, size[0]]),
                maxs - np.array([0, size[0], 0]),
                maxs - np.array([0, size[0], size[0]])
                ]
            )


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
        self.projo.v_rotation(-45.)

        self.fps_limitation = 60    #Hz
        self.last_time      = time.time()
        self.label          = "3D cube"

        #Shaders
        self.sh_cube            = sh.shader()
        self.sh_shadows         = sh.shader()
        self.sh_back_shadows    = sh.shader()
        self.sh_trajects        = sh.shader()

        #Trajectory data
        self.data = tr.data()

        #Global display data
        self.cube_vertices      = wire_cube(np.array([-.5,0,-.5]),
                                            np.array([.5,1,.5]))
        self.trajects_vertices  = np.array([[0,-1,0,0],
                                            [0,1,0,0]])#[time, lon, lat, ele]
        self.trajects_colors    = np.array([[0,0,0,1], [0,0,0,1]])
        self.thickness_of_backs  = 8 #pixels

        self.debug = False

    def init(self):
        self.mouse = [ 0, 0 ]
        self.imode = 'none'
        glEnable(GL_MULTISAMPLE)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
        if self.debug:
            print('\n-------------------------')
            print('Inits')
        self.init_shaders()
        if self.debug:
            print('-------------------------')

    def init_shaders(self):

        glsl_version = glGetString(GL_SHADING_LANGUAGE_VERSION).decode("utf-8")
        glsl_version = glsl_version.replace('.', '')

        ##########################
        # general vertex array object
        if self.debug:
            print('\t\33[1;32mGenerating vao...\33[m', end='')
        sys.stdout.flush()
        try:
            vao = glGenVertexArrays(1)
            glBindVertexArray(vao)
            if self.debug:
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
        self.vbo_cube               = glGenBuffers(1)
        self.vbo_trajects_vertices  = glGenBuffers(1)
        self.vbo_trajects_colors    = glGenBuffers(1)
        self.attr_cube_vertices     = sh.new_attribute_index()
        self.attr_trajects_vertices = sh.new_attribute_index()
        self.attr_trajects_colors   = sh.new_attribute_index()

        ##########################
        # Shaders
        #-----------------------------------------------
        # Cube
        ## CALLBACKS -------
        def _update_cube_arrays():
            sh.bind(self.vbo_cube, self.cube_vertices, self.attr_cube_vertices, 3, GL_FLOAT)
        self.update_cube_arrays = _update_cube_arrays

        def cube_display():
            self.sh_cube.update_projections(self.projo.projection(), self.projo.modelview())
            glDrawArrays(GL_LINES, 0, len(self.cube_vertices))
        self.sh_cube.display = cube_display

        ## CALLBACKS -------
        self.update_cube_arrays()

        # Loading shader files
        if self.debug:
            print('\t\33[1;32mCube shader...\33[m', end='')
        sys.stdout.flush()
        self.sh_cube.sh = sh.create(str(self.spacetimecube_dir / 'shaders/cube.vert'),
                                    None,
                                    str(self.spacetimecube_dir / 'shaders/cube.frag'),
                                    [self.attr_cube_vertices], ['in_vertex'],
                                    glsl_version)
        if not self.sh_cube.sh: exit(1)
        if self.debug:
            print('\t\tOk')
        sys.stdout.flush()
        #-----------------------------------------------

        #-----------------------------------------------
        # Shadows
        ## CALLBACKS -------
        def _update_trajects_arrays():
            sh.bind(self.vbo_trajects_vertices, self.trajects_vertices, self.attr_trajects_vertices, 4, GL_FLOAT)
            sh.bind(self.vbo_trajects_colors, self.trajects_colors, self.attr_trajects_colors, 4, GL_FLOAT)
        self.update_trajects_arrays = _update_trajects_arrays

        def shadows_display():
            self.sh_shadows.update_uniforms()
            self.sh_shadows.update_projections(self.projo.projection(), self.projo.modelview())
            glDrawArrays(GL_LINE_STRIP, 0, len(self.trajects_vertices))
        self.sh_shadows.display = shadows_display

        def update_uni_shadows():
            self.sh_shadows.set_uniform("maxs", self.data.maxs, '4fv')
            self.sh_shadows.set_uniform("mins", self.data.mins, '4fv')
        self.sh_shadows.update_uniforms = update_uni_shadows
        ## CALLBACKS -------

        # Loading shader files
        if self.debug:
            print('\t\33[1;32mShadows shader...\33[m', end='')
        sys.stdout.flush()
        self.sh_shadows.sh = sh.create( str(self.spacetimecube_dir / 'shaders/shadows.vert'),
                                        None,
                                        str(self.spacetimecube_dir / 'shaders/shadows.frag'),
                                        [self.attr_trajects_vertices, self.attr_trajects_colors],
                                        ['in_vertex', 'in_color'],
                                        glsl_version)

        if not self.sh_shadows.sh: exit(1)
        if self.debug:
            print('\tOk')
        sys.stdout.flush()
        #-----------------------------------------------

        #-----------------------------------------------
        # Back Shadows
        ## CALLBACKS -------
        def back_shadows_display():
            self.sh_back_shadows.update_uniforms()
            self.sh_back_shadows.update_projections(self.projo.projection(), self.projo.modelview())
            glDrawArrays(GL_LINE_STRIP_ADJACENCY, 0, len(self.trajects_vertices))
        self.sh_back_shadows.display = back_shadows_display

        def update_uni_back_shadows():
            h       = self.projo.near*math.tan(self.projo.v_angle/2.0)
            p_size  = h*2/(self.height)
            self.sh_back_shadows.set_uniform("pixel_size", p_size, 'f')
            self.sh_back_shadows.set_uniform("nb_pixels", self.thickness_of_backs, 'i')
            self.sh_back_shadows.set_uniform("cam_near", self.projo.near, 'f')
            self.sh_back_shadows.set_uniform("cam_pos", self.projo.position, '3fv')
            self.sh_back_shadows.set_uniform("maxs", self.data.maxs, '4fv')
            self.sh_back_shadows.set_uniform("mins", self.data.mins, '4fv')
        self.sh_back_shadows.update_uniforms = update_uni_back_shadows
        ## CALLBACKS -------

        # Loading shader files
        if self.debug:
            print('\t\33[1;32mBack shadows shader...\33[m', end='')
        sys.stdout.flush()
        self.sh_back_shadows.sh = sh.create(str(self.spacetimecube_dir / 'shaders/back_shadows.vert'),
                                            str(self.spacetimecube_dir / 'shaders/back_shadows.geom'),
                                            str(self.spacetimecube_dir / 'shaders/back_shadows.frag'),
                                            [self.attr_trajects_vertices, self.attr_trajects_colors],
                                            ['in_vertex', 'in_color'],
                                            glsl_version)

        if not self.sh_back_shadows.sh: exit(1)
        if self.debug:
            print('\tOk')
        sys.stdout.flush()
        #-----------------------------------------------

        #-----------------------------------------------
        # Main trajectories
        ## CALLBACKS -------
        def trajects_display():
            self.sh_trajects.update_uniforms()
            self.sh_trajects.update_projections(self.projo.projection(), self.projo.modelview())
            glDrawArrays(GL_LINE_STRIP, 0, len(self.trajects_vertices))
        self.sh_trajects.display = trajects_display

        def update_uni_trajects():
            self.sh_trajects.set_uniform("maxs", self.data.maxs, '4fv')
            self.sh_trajects.set_uniform("mins", self.data.mins, '4fv')
        self.sh_trajects.update_uniforms = update_uni_trajects
        ## CALLBACKS -------

        # Loading shader files
        if self.debug:
            print('\t\33[1;32mTrajects shader...\33[m', end='')
        sys.stdout.flush()
        self.sh_trajects.sh = sh.create(str(self.spacetimecube_dir / 'shaders/trajects.vert'),
                                        None,
                                        str(self.spacetimecube_dir / 'shaders/trajects.frag'),
                                        [self.attr_trajects_vertices, self.attr_trajects_colors],
                                        ['in_vertex', 'in_color'],
                                        glsl_version)

        if not self.sh_trajects.sh: exit(1)
        if self.debug:
            print('\tOk')
        sys.stdout.flush()

        #-----------------------------------------------

    def load_data(self, chunk=[], file=''):
        if len(chunk) >0:
            self.data.add(chunk)
        elif file != '':
            if self.debug:
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
            if self.debug:
                print('\t\tOk')
        sys.stdout.flush()

        #self.data.print_meta()
        self.trajects_vertices, self.trajects_colors = np.array(self.data.compute_geometry())
        self.update_trajects_arrays()
        self.update_cube()

    def clean_data(self):
        if self.debug:
            print('\33[1;32m\tCleaning data...\33[m', end='')
        self.data.clean()
        if self.debug:
            print('\tOk')

    def update_cube(self):
        self.update_cube_arrays()

    def display(self):
        glClearColor(.31,.63,1.0,1.0)
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)
        sh.display_list([   self.sh_cube,
                            self.sh_back_shadows,
                            self.sh_shadows,
                            self.sh_trajects])

    def on_mouse_click(self, button, state, x, y):
        self.mouse = [x, y]
        LEFT_BUTTON = 0
        MIDDLE_BUTTON = 1
        RIGHT_BUTTON = 2
        DOWN = 0
        UP = 1
        if button == LEFT_BUTTON and state == DOWN:
            self.imode = 'rotation'
        elif button == RIGHT_BUTTON and state == DOWN:
            self.imode = 'translation'
        elif state == UP:
            self.imode = 'none'

    def on_mouse_motion(self, x, y):
        dx, dy = x - self.mouse[0], y - self.mouse[1]
        if self.imode == 'rotation':
            self.projo.h_rotation(-dx/self.width*math.pi*2)
            self.projo.v_rotation(-dy/self.height*math.pi*2)
        elif self.imode == 'translation':
            d = np.linalg.norm(np.array(self.projo.viewpoint) - np.array(self.projo.position))
            self.projo.translate([-dx*d/1000, dy*d/1000])
        self.mouse = [x, y]

    def on_key_press(self, key, x, y):
        if key == b'\x1b':
            sys.exit()
        elif key == b't':
            self.clean_data()
        elif key == b'w':
            self.projo.wiggle = not self.projo.wiggle

    def on_resize(self, w, h):
        glViewport(0,  0,  w,  h);
        self.projo.change_ratio(w/float(h))
        self.width, self.height = w, h

    def animation(self):
        if self.projo.wiggle:
            self.projo.wiggle_next()
