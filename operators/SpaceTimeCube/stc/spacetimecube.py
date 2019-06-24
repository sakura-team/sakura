#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#Michael ORTEGA for PIMLIG/LIG/CNRS- 10/12/2018

import sys, math, time, datetime, copy
import numpy    as      np
from PIL        import  Image

try:
    from sakura.common.gpu import SAKURA_GPU_PERFORMANCE
except:
    SAKURA_GPU_PERFORMANCE = 'high'

try:
    from OpenGL.GL      import *
    from OpenGL.GLU     import *
    from OpenGL.GL      import shaders
except:
    print ('''ERROR: PyOpenGL not installed properly. ** ''')

from .libs import shader        as sh
from .libs import projector     as pr
from .libs import trajectory    as tr
from .libs import mercator      as mc
from .libs import tilenames     as tn
from .libs import geomaths      as gm

from .libs.display_objs import cube         as obj_cube
from .libs.display_objs import lines        as obj_lines
from .libs.display_objs import quad         as obj_quad
from .libs.display_objs import trajectories as obj_trajs
from .libs.display_objs import floor        as obj_fl
from .libs.display_objs import floor_shape  as obj_fs

class SpaceTimeCube:
    def __init__(self, op_dir):
        # import local libs
        self.spacetimecube_dir = op_dir / 'stc'

        self.projo = pr.projector(position = [0, 0, 2])
        #self.projo.v_rotation(-45.)

        self.label          = "3D cube"

        #Shaders
        self.sh_shadows         = sh.shader()
        self.sh_back_shadows    = sh.shader()
        self.sh_back_trajects   = sh.shader()

        #Trajectory data
        self.data = tr.data()

        #Global display data
        self.cube   = obj_cube.cube(np.array([-.5,0,-.5]), np.array([.5,1,.5]))
        self.lines  = obj_lines.lines()
        self.quad   = obj_quad.quad()
        self.trajs  = obj_trajs.trajectories()
        self.floor  = obj_fl.floor()
        self.fshapes= obj_fs.floor_shapes()

        self.trajs.geometry(self.data)

        #Display params
        self.width = 100
        self.height = 100
        self.projo.wiggle = False
        self.thickness_of_backs = 8 #pixels
        self.hovered_target     = -1
        self.selected_trajects  = []
        self.displayed_trajects = []
        self.new_selections     = []
        self.debug              = False
        self.current_point      = None
        self.colors_file        = None
        self.floor_shapes_file  = None

    def init(self):
        self.mouse = [ -1, -1 ]
        self.imode = 'none'
        self.cube.reset()
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
            print('Running')

    def init_shaders(self):

        glsl_version = glGetString(GL_SHADING_LANGUAGE_VERSION).decode("utf-8")
        glsl_version = glsl_version.replace('.', '').split()[0]

        # Loading shader files
        def load_shader(shader_name, shader, obj):
            if self.debug:
                print('\t\33[1;32m'+shader_name+' shader...\33[m', end='')
            sys.stdout.flush()
            shader.sh = obj.create_shader(str(self.spacetimecube_dir / 'shaders/'), glsl_version)

            if not shader.sh: exit(1)
            if self.debug:
                print('\t\tOk')
            sys.stdout.flush()

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

        ##########################
        # shaders

        #-----------------------------------------------
        # cube
        def update_uni_cube(_sh):
            _sh.set_uniform("cube_height", self.cube.height, 'f')
            _sh.set_uniform("maxs", self.data.maxs, '4fv')
            _sh.set_uniform("mins", self.data.mins, '4fv')
            _sh.set_uniform("projection_mat", self.projo.projection().T, 'm4fv')
            _sh.set_uniform("modelview_mat", self.projo.modelview().T, 'm4fv')
        self.cube.update_uniforms = update_uni_cube
        self.cube.generate_buffers_and_attributes()
        self.cube.update_arrays()
        load_shader('Cube', self.cube.sh, self.cube)

        #-----------------------------------------------

        #-----------------------------------------------
        # lines
        self.lines.update_uniforms = update_uni_cube
        self.lines.generate_buffers_and_attributes()
        self.lines.update_arrays()
        load_shader('Lines', self.lines.sh, self.lines)
        #-----------------------------------------------

        #-----------------------------------------------
        # quad
        self.quad.update_uniforms = update_uni_cube
        self.quad.generate_buffers_and_attributes()
        self.quad.update_arrays()
        load_shader('Quad', self.quad.sh, self.quad)
        #-----------------------------------------------

        #-----------------------------------------------
        # main trajectories
        self.trajs.update_uniforms = update_uni_cube
        self.trajs.generate_buffers_and_attributes()
        self.trajs.update_arrays()
        load_shader('Trajs', self.trajs.sh, self.trajs)
        #-----------------------------------------------

        #-----------------------------------------------
        # floor shapes
        self.fshapes.update_uniforms = update_uni_cube
        self.fshapes.generate_buffers_and_attributes()
        self.fshapes.update_arrays()
        load_shader('FShap', self.fshapes.sh, self.fshapes)
        #-----------------------------------------------


        #-----------------------------------------------
        # Floor
        def update_uni_floor(_sh):
            _sh.set_uniform("cube_height", self.cube.height, 'f')
            _sh.set_uniform("maxs", self.data.maxs, '4fv')
            _sh.set_uniform("mins", self.data.mins, '4fv')
            _sh.set_uniform("projection_mat", self.projo.projection().T, 'm4fv')
            _sh.set_uniform("modelview_mat", self.projo.modelview().T, 'm4fv')
            _sh.set_uniform("floor_texture", 0, 'i')
        self.floor.update_uniforms = update_uni_floor
        self.floor.generate_buffers_and_attributes()
        self.floor.update_texture()
        self.floor.update_arrays()
        load_shader('Floor', self.floor.sh, self.floor)
        #-----------------------------------------------


        #-----------------------------------------------
        # shadows
        def shadows_display():
            self.sh_shadows.update_uniforms(self.sh_shadows)
            glDrawArrays(GL_LINE_STRIP, 0, len(self.trajs.vertices))
        self.sh_shadows.display = shadows_display

        self.sh_shadows.update_uniforms = update_uni_cube

        # Loading shader files
        if self.debug:
            print('\t\33[1;32mShadows shader...\33[m', end='')
        sys.stdout.flush()
        self.sh_shadows.sh = sh.create( str(self.spacetimecube_dir / 'shaders/shadows.vert'),
                                        None,
                                        str(self.spacetimecube_dir / 'shaders/shadows.frag'),
                                        [self.trajs.attr_vertices, self.trajs.attr_colors],
                                        ['in_vertex', 'in_color'],
                                        glsl_version)

        if not self.sh_shadows.sh: exit(1)
        if self.debug:
            print('\tOk')
        sys.stdout.flush()
        #-----------------------------------------------

        #-----------------------------------------------
        # back shadows
        ## CALLBACKS -------
        def back_shadows_display():
            self.sh_back_shadows.update_uniforms()
            glDrawArrays(GL_LINE_STRIP_ADJACENCY, 0, len(self.trajs.vertices))
        self.sh_back_shadows.display = back_shadows_display

        def update_uni_back_shadows():
            h       = self.projo.near*math.tan(self.projo.v_angle/2.0)
            p_size  = h*2/(self.height)
            self.sh_back_shadows.set_uniform("cube_height", self.cube.height, 'f')
            self.sh_back_shadows.set_uniform("pixel_size", p_size, 'f')
            self.sh_back_shadows.set_uniform("nb_pixels", self.thickness_of_backs, 'i')
            self.sh_back_shadows.set_uniform("cam_near", self.projo.near, 'f')
            self.sh_back_shadows.set_uniform("cam_pos", self.projo.position, '3fv')
            self.sh_back_shadows.set_uniform("maxs", self.data.maxs, '4fv')
            self.sh_back_shadows.set_uniform("mins", self.data.mins, '4fv')
            self.sh_back_shadows.set_uniform("projection_mat", self.projo.projection().T, 'm4fv')
            self.sh_back_shadows.set_uniform("modelview_mat", self.projo.modelview().T, 'm4fv')
        self.sh_back_shadows.update_uniforms = update_uni_back_shadows
        ## CALLBACKS -------

        # Loading shader files
        if self.debug:
            print('\t\33[1;32mBack shadows shader...\33[m', end='')
        sys.stdout.flush()
        if SAKURA_GPU_PERFORMANCE != 'low':
            self.sh_back_shadows.sh = sh.create(str(self.spacetimecube_dir / 'shaders/back_shadows.vert'),
                                                str(self.spacetimecube_dir / 'shaders/back_shadows.geom'),
                                                str(self.spacetimecube_dir / 'shaders/back_shadows.frag'),
                                                [self.trajs.attr_vertices, self.trajs.attr_colors],
                                                ['in_vertex', 'in_color'],
                                                glsl_version)

            if not self.sh_back_shadows.sh: exit(1)
        if self.debug:
            print('\tOk')
        sys.stdout.flush()
        #-----------------------------------------------

        #-----------------------------------------------
        # back trajectories
        def back_trajects_display():
            self.sh_back_trajects.update_uniforms()
            glDrawArrays(GL_LINE_STRIP_ADJACENCY, 0, len(self.trajs.vertices))
        self.sh_back_trajects.display = back_trajects_display

        def update_uni_back_trajects():
            h       = self.projo.near*math.tan(self.projo.v_angle/2.0)
            p_size  = h*2/(self.height)
            self.sh_back_trajects.set_uniform("cube_height", self.cube.height, 'f')
            self.sh_back_trajects.set_uniform("pixel_size", p_size, 'f')
            self.sh_back_trajects.set_uniform("nb_pixels", self.thickness_of_backs, 'i')
            self.sh_back_trajects.set_uniform("cam_near", self.projo.near, 'f')
            self.sh_back_trajects.set_uniform("cam_pos", self.projo.position, '3fv')
            self.sh_back_trajects.set_uniform("maxs", self.data.maxs, '4fv')
            self.sh_back_trajects.set_uniform("mins", self.data.mins, '4fv')
            self.sh_back_trajects.set_uniform("projection_mat", self.projo.projection().T, 'm4fv')
            self.sh_back_trajects.set_uniform("modelview_mat", self.projo.modelview().T, 'm4fv')
        self.sh_back_trajects.update_uniforms = update_uni_back_trajects

        # Loading shader files
        if self.debug:
            print('\t\33[1;32mBack trajects shader...\33[m', end='')
        sys.stdout.flush()
        if SAKURA_GPU_PERFORMANCE != 'low':
            self.sh_back_trajects.sh = sh.create(str(self.spacetimecube_dir / 'shaders/back_trajects.vert'),
                                                str(self.spacetimecube_dir / 'shaders/back_trajects.geom'),
                                                str(self.spacetimecube_dir / 'shaders/back_trajects.frag'),
                                                [self.trajs.attr_vertices, self.trajs.attr_colors],
                                                ['in_vertex', 'in_color'],
                                                glsl_version)

            if not self.sh_back_trajects.sh: exit(1)
        if self.debug:
            print('\tOk')
        sys.stdout.flush()
        #-----------------------------------------------


    def load_data(self, chunk=[], file=''):

        if self.colors_file:
            self.data.colors_file = self.colors_file
            self.trajs.display_color = 'semantic'

        if len(chunk) > 0:
            self.data.add(chunk)
        elif file != '':
            if self.debug:
                print('\t\33[1;32mReading data...\33[m', end='')
            sys.stdout.flush()
            big_chunk = np.recfromcsv(file, delimiter=',', encoding='utf-8')

            if type(big_chunk[0][1]) != int:
                #convert
                for i in range(len(big_chunk)):
                    d = big_chunk[i][1]
                    if d.find('24:00') != -1:
                        d = d.replace('24:00', '23:59')
                    d = datetime.datetime.strptime(d, '%Y-%m-%d %H:%M:%S')
                    big_chunk[i][1] = int(d.strftime("%s"))

                #change type
                dt = big_chunk.dtype
                dt = dt.descr
                dt[0] = ('trajectory', np.dtype('<U8'))
                dt[1] = ('date', np.dtype('int'))
                big_chunk = big_chunk.astype(dt)

            self.data.add(big_chunk[ : int(len(big_chunk)/2)])
            self.data.add(big_chunk[int(len(big_chunk)/2) : ])
            if self.debug:
                print('\t\tOk')
        sys.stdout.flush()

        #self.data.print_meta()
        self.trajs.geometry(self.data)
        self.trajs.update_arrays()
        if self.fshapes.displayed and self.floor_shapes_file:
            self.fshapes.geometry(self.data)
            self.fshapes.update_arrays()
            self.data.maxs[1:3] = np.max(self.fshapes.vertices, axis=0)[1:3]
            self.data.mins[1:3] = np.min(self.fshapes.vertices, axis=0)[1:3]
        self.update_cube_and_lines()
        self.send_new_dates()

    def get_trajectories(self):
        return self.data.trajects_names

    def clean_data(self):
        if self.debug:
            print('\33[1;32m\tCleaning data...\33[m', end='')
        self.data.clean()
        if self.debug:
            print('\tOk')

    def compute_proj_cube_corners(self):

        m = [self.mouse[0], self.height - self.mouse[1]]
        size =  [   self.data.maxs[1] - self.data.mins[1],
                    self.data.maxs[2] - self.data.mins[2] ]
        self.cube.compute_proj_corners(size, m, self.projo, [self.width, self.height])
        self.update_cube_and_lines()


    def update_cube_and_lines(self):
        self.cube.update_arrays()
        self.lines.update_arrays()

    def compute_closest_color(self, edge_size):
        '''Reads a square from the framebuffer,
            and returns id of the closest color'''
        pixels = glReadPixels(self.mouse[0]-edge_size/2, self.height-self.mouse[1]-edge_size/2, edge_size, edge_size, GL_RGB, GL_UNSIGNED_BYTE)
        pixels = np.reshape(bytearray(pixels), (edge_size,edge_size,3))
        cp  = []
        cpo = []
        white = gm.color_to_id(np.array([1,1,1]))
        for i in range(0,edge_size):
            for j in range(0,edge_size):
                if gm.color_to_id(pixels[i][j]/255.0) < white:
                    cp.append([i,j])
                    cpo.append([edge_size/2, edge_size/2])

        if len(cp) == 0:
            return -1

        xs, ys = (np.array(cp) - np.array(cpo)).T
        pos = cp[np.argmin(np.hypot(xs,ys))]
        id = gm.color_to_id(np.append(pixels[pos[0]][pos[1]],1)/255.0)
        try:
            return id
        except:
            return -1

    def compute_hovered_target(self):
        glClearColor(1.0,1.0,1.0,1.0)
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)

        glDisable(GL_MULTISAMPLE)
        self.trajs.update_arrays('trajectories')
        sh.display_list([self.trajs.sh])
        ccolor = self.compute_closest_color(10)
        t_indice = -1
        if ccolor != -1 and ccolor in self.data.trajects_ids:
            t_indice = self.data.trajects_ids.index(ccolor)

        if self.trajs.display_color != 'trajectories':
            self.trajs.update_arrays()

        glEnable(GL_MULTISAMPLE)
        return t_indice

    def compute_hovered_point(self, traject):
        '''Here we compute the closest trajectory point from the mouse'''
        glClearColor(1.0,1.0,1.0,1.0)
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)
        glDisable(GL_MULTISAMPLE)

        #extracting arrays
        t_ind = self.data.trajects[traject].display_indice
        t_len = len(self.data.trajects[traject].points)

        cop_vertices = copy.copy(self.trajs.vertices)
        cop_colors = copy.copy(self.trajs.colors)
        self.trajs.vertices = self.trajs.vertices[t_ind +1: t_ind +t_len +1]
        self.trajs.colors = self.trajs.basic_colors_list[0: len(self.trajs.vertices)]

        self.trajs.update_arrays('trajectories')
        sh.display_list([self.sh_shadows, self.trajs.sh])
        p_indice = self.compute_closest_color(10)

        self.trajs.vertices = copy.copy(cop_vertices)
        self.trajs.colors = copy.copy(cop_colors)
        self.trajs.update_arrays()

        glEnable(GL_MULTISAMPLE)
        return p_indice


    def update_transparency(self, indice, value):
        t_ind = self.data.trajects[indice].display_indice
        t_len = len(self.data.trajects[indice].points)
        arr = self.trajs.colors[t_ind+1: t_ind +1+ t_len]
        if len(arr) > 0:
            arr[:, 3] = value
            self.trajs.colors[t_ind+1: t_ind +1+ t_len] = arr

        sarr = self.trajs.sem_colors[t_ind+1: t_ind +1+ t_len]
        if len(sarr) > 0:
            sarr[:, 3] = value
            self.trajs.sem_colors[t_ind+1: t_ind +1+ t_len] = sarr


    def display(self):
        # Hovering
        if gm.pt_in_frame(self.mouse, [0, 0], [self.width, self.height]) and self.imode == 'none':
            t_indice = self.compute_hovered_target()

            if self.trajs.display_color == 'trajectories':
                #Highlighting the trajectory
                if t_indice != -1 and not t_indice in self.selected_trajects:
                    if self.hovered_target == -1:
                        self.update_transparency(t_indice, 0.5)
                    elif self.hovered_target != t_indice:
                        self.update_transparency(self.hovered_target, 1.0)
                        self.update_transparency(t_indice, 0.5)
                    self.hovered_target =  t_indice

                elif self.hovered_target != -1:
                    self.update_transparency(self.hovered_target, 1.0)
                    self.hovered_target =  -1

            self.trajs.update_arrays()

            lines_vertices = np.array([[0,0,0,0], [0,0,0,0]])
            quad_vertices = np.array([[0,0,0,0], [0,0,0,0], [0,0,0,0]])

            #Computing the closest point
            if t_indice != -1 and self.imode == 'none':
                p_indice = self.compute_hovered_point(t_indice)
                if p_indice != -1:
                    try:
                        pt = self.data.trajects[t_indice].points[p_indice]
                    except:
                        print(t_indice, len(self.data.trajects))
                        print(p_indice, len(self.data.trajects[t_indice].points))
                    lines_vertices = self.data.compute_line_vertices(pt)
                    quad_vertices = self.data.compute_quad_vertices(pt)
                    lon, lat = mc.lonlat_from_mercator(pt[1], pt[2])
                    self.current_point = [t_indice, p_indice]
                    self.app.push_event('hovered_gps_point', pt[0], lon, lat, pt[3], self.data.trajects_names[t_indice])
                    self.send_new_dates(th_value = pt[0])
            else:
                if self.current_point != None:
                    self.app.push_event('hovered_gps_point', -1, -1, -1, -1, '')
                    self.current_point = None


            self.lines.vertices = copy.copy(lines_vertices)
            self.lines.update_arrays()
            self.quad.vertices = copy.copy(quad_vertices)
            self.quad.update_arrays()

        if self.trajs.display_color != 'trajectories':
            for i in range(len(self.data.trajects)):
                self.update_transparency(i, 0.5)
            self.trajs.update_arrays()

        #Selection
        if len(self.new_selections):
            while len(self.new_selections):
                i = self.new_selections[0]
                if i not in self.selected_trajects:
                    self.update_transparency(i, 0.5)
                    self.selected_trajects.append(self.new_selections.pop(0))
                else:
                    self.update_transparency(i, 1.0)
                    index = self.selected_trajects.index(self.new_selections.pop(0))
                    self.selected_trajects.pop(index)
            self.trajs.update_arrays()

        # Main display
        glClearColor(.31,.63,1.0,1.0)
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)

        if self.cube.height > 0.00000000001:
            glDisable(GL_DEPTH_TEST)
            if SAKURA_GPU_PERFORMANCE == 'low':
                sh.display_list([ self.floor.sh ])
            else:
                sh.display_list([   self.floor.sh,
                                    self.sh_back_shadows
                                ])
            glEnable(GL_DEPTH_TEST)

            sh.display_list([   self.sh_shadows])

            if SAKURA_GPU_PERFORMANCE != 'low':
                glDisable(GL_DEPTH_TEST)
                sh.display_list([   self.sh_back_trajects]);
                glEnable(GL_DEPTH_TEST)

        else:
            glDisable(GL_DEPTH_TEST)
            if SAKURA_GPU_PERFORMANCE == 'low':
                sh.display_list([ self.floor.sh ])
            else:
                sh.display_list([   self.floor.sh,
                                    self.sh_back_trajects
                                ])
            glEnable(GL_DEPTH_TEST)

        if self.fshapes.displayed and self.floor_shapes_file:
            sh.display_list([   self.fshapes.sh])

        sh.display_list([   self.cube.sh])
        if self.cube.height > 0.00000000001:
            sh.display_list([   self.quad.sh])
        sh.display_list([   self.trajs.sh])

        glDisable(GL_DEPTH_TEST)
        sh.display_list([ self.lines.sh])
        glEnable(GL_DEPTH_TEST)


    def send_new_dates(self, th_value = None):
        if len(self.cube.proj_corners_bottom):
            times = [   {'time': self.data.mins[0],
                            'x': self.cube.proj_corners_bottom[0][0],
                            'y': self.cube.proj_corners_bottom[0][1]},
                        {'time': self.data.maxs[0],
                            'x': self.cube.proj_corners_up[0][0],
                            'y': self.cube.proj_corners_up[0][1]} ]

            if th_value:
                inter = (th_value - self.data.mins[0])/(self.data.maxs[0] - self.data.mins[0])
                traj_size = [   self.data.maxs[1] - self.data.mins[1],
                                self.data.maxs[2] - self.data.mins[2] ]
                ppi = self.cube.project_corner( [.5, inter,.5],
                                                traj_size,
                                                self.projo,
                                                [self.width, self.height])
                times.append({'time': th_value, 'x': ppi[0],'y': ppi[1]})
            else:
                times.append({'time': self.data.mins[0],
                                'x': self.cube.proj_corners_bottom[0][0],
                                'y': self.cube.proj_corners_bottom[0][1]})

            self.app.push_event('times_and_positions', times)
            return times
        else:
            return []

    def update_floor(self):
        self.floor.update(self.data.mins, self.data.maxs, debug=True)

    def on_mouse_click(self, button, state, x, y):
        self.mouse = [x, y]
        LEFT_BUTTON = 0
        MIDDLE_BUTTON = 1
        RIGHT_BUTTON = 2
        DOWN = 0
        UP = 1

        #projecting cube corners
        self.compute_proj_cube_corners()

        if state == UP: #leaving any interaction modes
            self.cube.reset()
            self.imode = 'none'
            return

        if self.cube.current_edge == -1: #Not on an edge !!!
            if button == LEFT_BUTTON and state == DOWN:
                self.imode = 'rotation'
            elif button == RIGHT_BUTTON and state == DOWN:
                self.imode = 'translation'
        else:   #On an edge !!!!
            if button == LEFT_BUTTON and state == DOWN:
                self.imode = 'scale'
            elif button == RIGHT_BUTTON and state == DOWN:
                self.imode = self.cube.crop_mode(self.mouse)

    def on_mouse_motion(self, x, y):
        #if self.imode == 'none':
        self.compute_proj_cube_corners()

        dx, dy = x - self.mouse[0], y - self.mouse[1]

        if self.imode == 'rotation':
            self.projo.h_rotation(-dx/self.width*math.pi*2)
            self.projo.v_rotation(-dy/self.height*math.pi*2)
            self.send_new_dates()

        elif self.imode == 'translation':
            d = np.linalg.norm(np.array(self.projo.viewpoint) - np.array(self.projo.position))
            self.projo.translate([-dx*d/1000, dy*d/1000])
            self.send_new_dates()

        elif self.imode == 'scale':
            self.cube.scale([dx,dy])
            self.send_new_dates()

        elif self.imode in ['crop_down', 'crop_up']:
            print(self.imode, 'not yet implemented')

        self.mouse = [x, y]

    def on_wheel(self, delta):
        self.projo.zoom(-delta/10.)

    def on_key_press(self, key, x, y):
        if key == b'\x1b':
            sys.exit()
        elif key == b's':
            self.trajs.display_color = 'semantic'
        elif key == b'S':
            self.trajs.display_color = 'trajectories'
        elif key == b't':
            self.floor.update()
        elif key == b'w':
            self.toggle_wiggle(not self.projo.wiggle)
        elif key == b'+':
            self.projo.zoom(1)
        elif key == b'-':
            self.projo.zoom(-1)
        elif key == b'D':
            self.set_floor_darkness(self.floor.darkness+.1)
        elif key == b'd':
            self.set_floor_darkness(self.floor.darkness-.1)
        elif key == b'h':
            self.set_cube_height(self.cube.height-.1)
        elif key == b'H':
            self.set_cube_height(self.cube.height+.1)
        elif key == b'p':
            self.data.print_meta()
        elif key == b'f':
            self.update_floor()
        elif int(key) in range(0,10):
            if not int(key) in self.selected_trajects:
                self.select_trajectories([int(key)])
            else:
                self.unselect_trajectories([int(key)])
        else:
            print('\33[1;32m\tUnknown key\33[m', key)

    def on_resize(self, w, h):
        glViewport(0,  0,  w,  h);
        self.projo.change_ratio(w/float(h))
        self.width, self.height = w, h

    def animation(self):
        if self.projo.wiggle:
            self.projo.wiggle_next()

    def toggle_wiggle(self, value= bool):
        print('W val', value)
        if value != None:
            self.projo.wiggle = value
        else:
            self.projo.wiggle = not self.projo.wiggle
        print('wiggle', self.projo.wiggle )

    def is_wiggle_on(self):
        return self.projo.wiggle

    def set_cube_height(self, value):
        self.cube.set_height(value)

    def set_floor_darkness(self, value):
        self.floor.set_darkness(value)

    def set_colors_file(self, fname):
        self.colors_file = fname

    def set_floor_shape_file(self, fname):
        if self.debug:
            print('\t\33[1;32mReading floor shape...\33[m', end='')
        self.floor_shapes_file = fname
        self.fshapes.read_shapes(fname)
        if self.debug:
            print('\tOk')

    def select_colored_semantic(self, index):
        self.data.update_sem_colors(index)
        self.trajs.geometry(self.data)
        self.trajs.update_arrays()

    def get_semantic_names(self):
        return self.data.get_semantic_names()

    def get_map_layers(self):
        return self.floor.get_layers()

    def set_map_layer(self, layer):
        if layer in self.floor.get_layers():
            self.floor.layer = layer
        else:
            return 'Unkown map layer !!!'

        self.update_floor()
        return

    def select_trajectories(self, l):
        for i in l:
            if i >= 0 and i < len(self.data.trajects):
                if i not in self.selected_trajects:
                    self.new_selections.append(i)
            else:
                print('\t\33[1;31mTrajectory index out of range !!!\33[m')

    def unselect_trajectories(self, l):
        for i in l:
            if i >= 0 and i < len(self.data.trajects):
                if i in self.selected_trajects:
                    self.new_selections.append(i)
            else:
                print('\t\33[1;31mTrajectory index out of range !!!\33[m')

    def hide_trajectories(self, l):
        print('hide', l)
        if len(l):
            for id in l:
                if id >= 0 and id < len(self.data.trajects):
                    if id in self.data.displayed:
                        index = self.data.displayed.index(id)
                        self.data.displayed.pop(index)
                        self.trajs.geometry(self.data)
            self.data.make_meta()
            self.trajs.update_arrays()
            self.update_cube_and_lines()

    def show_trajectories(self, l):
        if len(l):
            for id in l:
                if id >= 0 and id < len(self.data.trajects):
                    if id not in self.data.displayed:
                        self.data.displayed.append(id)
                        self.data.displayed.sort()
                        self.trajs.geometry(self.data)
            self.data.make_meta()
            self.trajs.update_arrays()
            self.update_cube_and_lines()
