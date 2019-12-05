#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#Michael ORTEGA for PIMLIG/LIG/CNRS- 10/12/2018

import sys, math, time, inspect, datetime, copy
import numpy    as      np
from pathlib    import  Path
from PIL        import  Image

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
from .libs import geo_shapes    as gs

from .libs.display_objs import cube             as obj_cube
from .libs.display_objs import lines            as obj_lines
from .libs.display_objs import quad             as obj_quad
from .libs.display_objs import trajectories     as obj_trajs
from .libs.display_objs import floor            as obj_fl
from .libs.display_objs import floor_shapes     as obj_fs



class SpaceTimeCube:
    def __init__(self):

        try:
            from sakura.common.gpu import SAKURA_GPU_PERFORMANCE
            self.SAKURA_GPU_PERFORMANCE = 'high'
        except:
            self.SAKURA_GPU_PERFORMANCE = 'low'

        # import local libs
        spacetimecube_py_path = Path(inspect.getabsfile(self.__class__))
        self.spacetimecube_dir = spacetimecube_py_path.parent

        self.projo = pr.projector(position = [0,0,2], viewpoint= [0,0,0])

        self.label          = "3D cube"
        self.verbose        = False

        #Shaders
        self.sh_shadows         = sh.shader()
        self.sh_back_shadows    = sh.shader()
        self.sh_back_trajects   = sh.shader()

        #Trajectory data
        self.data       = tr.data()
        self.geo_shapes = gs.geo_shapes()
        self.date_format= '%Y-%m-%d %H:%M:%S'

        #Global display data
        self.cube       = obj_cube.cube(np.array([-.5,0,-.5]), np.array([.5,1,.5]))
        self.lines      = obj_lines.lines()
        self.quad       = obj_quad.quad()
        self.trajs      = obj_trajs.trajectories()
        self.floor      = obj_fl.floor()
        self.fcontours  = obj_fs.contours()
        self.fareas     = obj_fs.areas()

        self.trajs.geometry(self.data)

        #Display params
        self.width = 100
        self.height = 100
        self.projo.wiggle = False
        self.thickness_of_backs = 4 #pixels
        self.hovered_target     = -1
        self.selected_trajects  = []
        self.displayed_trajects = []
        self.new_selections     = []
        self.debug              = False
        self.current_point      = None
        self.colors_file        = None
        self.floor_shapes_file  = None
        self.display_shadows    = True
        self.selection_activated = True
        self.back_color         = [.31,.63,1.0,1.0]
        self.trajects_width      = 1

    def init(self):
        self.mouse = [ -1, -1 ]
        self.imode = 'none'
        self.idate = time.time()
        self.cube.reset()
        glEnable(GL_MULTISAMPLE)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

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
        # floor contours
        def update_uni_fcontours(_sh):
            _sh.set_uniform("cube_height", self.cube.height, 'f')
            _sh.set_uniform("maxs", self.data.maxs, '4fv')
            _sh.set_uniform("mins", self.data.mins, '4fv')
            _sh.set_uniform("curr_date", self.data.curr_floor_date, 'f')
            _sh.set_uniform("projection_mat", self.projo.projection().T, 'm4fv')
            _sh.set_uniform("modelview_mat", self.projo.modelview().T, 'm4fv')
        self.fcontours.update_uniforms = update_uni_fcontours
        self.fcontours.generate_buffers_and_attributes()
        self.fcontours.update_arrays()
        load_shader('FCont', self.fcontours.sh, self.fcontours)
        #-----------------------------------------------

        #-----------------------------------------------
        # floor areas
        self.fareas.update_uniforms = update_uni_fcontours
        self.fareas.generate_buffers_and_attributes()
        self.fareas.update_arrays()
        load_shader('FArea', self.fareas.sh, self.fareas)
        #-----------------------------------------------

        #-----------------------------------------------
        # Floor
        def update_uni_floor(_sh):
            _sh.set_uniform("cube_height", self.cube.height, 'f')
            _sh.set_uniform("maxs", self.data.maxs, '4fv')
            _sh.set_uniform("mins", self.data.mins, '4fv')
            _sh.set_uniform("curr_date", self.data.curr_floor_date, 'f')
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
            p_size  = h*2/(self.height)*self.trajects_width
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
        if self.SAKURA_GPU_PERFORMANCE != 'low':
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
            p_size  = h*2/(self.height)*self.trajects_width
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
        if self.SAKURA_GPU_PERFORMANCE != 'low':
            self.sh_back_trajects.sh = sh.create(str(self.spacetimecube_dir / 'shaders/back_trajects.vert'),
                                                str(self.spacetimecube_dir / 'shaders/back_trajects.geom'),
                                                str(self.spacetimecube_dir / 'shaders/back_trajects.frag'),
                                                [self.trajs.attr_vertices, self.trajs.attr_colors, self.trajs.attr_densities],
                                                ['in_vertex', 'in_color', 'in_density'],
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
                print('\t\33[1;32mReading data file...\33[m', end='')
                sys.stdout.flush()

            if self.verbose:
                print('\n\t\t\33[1;32mRec from csv...\33[m', end='')
                sys.stdout.flush()
            big_chunk = np.recfromcsv(file, delimiter=',', encoding='utf-8')
            if self.verbose:
                print('\t', len(big_chunk), 'lines')
                sys.stdout.flush()

            if type(big_chunk[0][1]) != int:

                #convert
                for i in range(len(big_chunk)):
                    if self.verbose:
                        print('\r\t\t\33[1;32mTimestamps to dates...\33[m '+str(int(i/len(big_chunk)*100))+'%', end='')
                        sys.stdout.flush()
                    d = big_chunk[i][1]
                    if d.find('24:00') != -1:
                        d = d.replace('24:00', '23:59')
                    try:
                        d = datetime.datetime.strptime(d, self.date_format)
                    except:
                        print('\n\nWRONG DATE FORMAT ', self.date_format, '\n\n')
                        sys.exit()

                    big_chunk[i][1] = int(d.strftime("%s"))
                if self.verbose:
                    print('\r\t\t\33[1;32mTimestamps to dates...\33[m 100%')
                    sys.stdout.flush()

                #change type
                dt = big_chunk.dtype
                dt = dt.descr
                dt[0] = ('trajectory', np.dtype('U64'))
                dt[1] = ('date', np.dtype('int'))
                big_chunk = big_chunk.astype(dt)

            nb_pieces = 20
            piece = int(len(big_chunk)/nb_pieces)

            start_t = time.time()
            curr_t = 0
            for i in range(nb_pieces-1):
                if self.verbose:
                    est_time = '...'
                    if i != 0:
                        est_time = str(int(curr_t/i*nb_pieces))+'s'
                    print('\r\t\t\33[1;32mLines to data structure...\33[m '+
                                str(int(i/nb_pieces*100))+
                                '%  (estimated time: '+est_time+')', end='')
                    sys.stdout.flush()
                self.data.add(big_chunk[ i*piece: (i+1)*piece], meta = False)
                curr_t = time.time() - start_t

            self.data.add(big_chunk[ (nb_pieces-1)*piece: ], meta = False)
            print('\r\t\t\33[1;32mLines to data structure...\33[m 100%')

            print('\r\t\33[1;32mMaking Meta...\33[m', end='')
            self.data.make_meta()
            print('\tOk')

        sys.stdout.flush()

        self.trajs.geometry(self.data)
        self.trajs.update_arrays()
        self.update_cube_and_lines()
        self.send_new_dates()
        self.update_geo_shapes()

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

        inter = (self.data.curr_date - self.data.mins[0])/(self.data.maxs[0] - self.data.mins[0])
        self.cube.proj_curr_pt  = self.cube.project_corner( [.5, inter,.5],
                                                            size,
                                                            self.projo,
                                                            [self.width, self.height])

    def update_geo_shapes(self):
        if self.geo_shapes.displayed and self.floor_shapes_file:
            self.fcontours.geometry(self.data, self.geo_shapes)
            self.fcontours.update_arrays()
            self.fareas.geometry(self.data, self.geo_shapes)
            self.fareas.update_arrays()
            nmax = np.max(self.fcontours.vertices, axis=0)[1:3]
            nmin = np.min(self.fcontours.vertices, axis=0)[1:3]
            self.data.maxs[1:3] = [max(nmax[0], self.data.maxs[1]), max(nmax[1], self.data.maxs[2])]
            self.data.mins[1:3] = [min(nmin[0], self.data.mins[1]), min(nmin[1], self.data.mins[2])]

    def update_cube_and_lines(self):
        self.cube.update_arrays()
        self.lines.update_arrays()

    def closest_color(self, edge_size):
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

    def hovered_trajectory(self):
        glClearColor(1.0,1.0,1.0,1.0)
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)

        glDisable(GL_MULTISAMPLE)
        glDisable(GL_BLEND)
        self.trajs.update_arrays('trajectories')
        if self.SAKURA_GPU_PERFORMANCE == 'low':
            sh.display_list([self.trajs.sh])
        else:
            sh.display_list([self.sh_back_trajects])

        vp = glGetInteger(GL_VIEWPORT)
        buffer = glReadPixels(0, 0, vp[2], vp[3], GL_RGB, GL_UNSIGNED_BYTE)
        image = Image.frombuffer('RGB', (vp[2], vp[3]), buffer, 'raw', 'RGB', 0, 1).transpose(Image.FLIP_TOP_BOTTOM)
        image.save('saved.png')

        ccolor = self.closest_color(10)
        t_indice = -1
        if ccolor != -1 and ccolor in self.data.trajects_ids:
            t_indice = self.data.trajects_ids.index(ccolor)

        if self.trajs.display_color != 'trajectories':
            self.trajs.update_arrays()

        glEnable(GL_BLEND)
        glEnable(GL_MULTISAMPLE)
        return t_indice

    def hovered_point(self, traject):
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
        #sh.display_list([self.sh_shadows, self.trajs.sh])
        sh.display_list([self.trajs.sh])
        p_indice = self.closest_color(10)

        self.trajs.vertices = copy.copy(cop_vertices)
        self.trajs.colors = copy.copy(cop_colors)
        self.trajs.update_arrays()

        glEnable(GL_MULTISAMPLE)
        return p_indice

    def display(self):
        # Hovering
        if gm.pt_in_frame(self.mouse, [0, 0], [self.width, self.height]) and self.imode == 'none':
            self.hovered_target = self.hovered_trajectory()

            lines_vertices = np.array([[0,0,0,0], [0,0,0,0]])
            quad_vertices = np.array([[0,0,0,0], [0,0,0,0], [0,0,0,0]])

            #Computing the closest point
            if self.hovered_target != -1 and self.imode == 'none':
                p_indice = self.hovered_point(self.hovered_target)
                if p_indice != -1:
                    try:
                        pt = self.data.trajects[self.hovered_target].points[p_indice]
                    except:
                        print(self.hovered_target, len(self.data.trajects))
                        print(p_indice, len(self.data.trajects[self.hovered_target].points))
                    lines_vertices = self.data.compute_line_vertices(pt)
                    quad_vertices = self.data.compute_quad_vertices(pt)
                    lon, lat = mc.lonlat_from_mercator(pt[1], pt[2])

                    self.data.curr_date = pt[0]
                    if self.floor.updatable_height:
                        self.data.curr_floor_date = pt[0]
                    else:
                        self.data.curr_floor_date = self.data.mins[0]
                    self.current_point = [self.hovered_target, p_indice]
                    self.app.push_event('hovered_gps_point', pt[0], lon, lat, pt[3], self.data.trajects_names[self.hovered_target])
                    self.send_new_dates()
            else:
                if self.current_point != None:
                    self.app.push_event('hovered_gps_point', -1, -1, -1, -1, '')
                    self.current_point = None
                    self.data.curr_floor_date = self.data.mins[0]
                    self.data.curr_date = self.data.mins[0]

            self.lines.vertices = copy.copy(lines_vertices)
            self.lines.update_arrays()
            self.quad.vertices = copy.copy(quad_vertices)
            self.quad.update_arrays()

        #Selection
        if len(self.new_selections):
            if len(self.new_selections):
                while len(self.new_selections):
                    i = self.new_selections[0]
                    if i not in self.selected_trajects:
                        self.selected_trajects.append(self.new_selections.pop(0))
                    else:
                        index = self.selected_trajects.index(self.new_selections.pop(0))
                        self.selected_trajects.pop(index)
                self.trajs.geometry(self.data, self.selected_trajects)
                self.trajs.update_arrays()


        # Main display
        glClearColor(*self.back_color)
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)

        if self.geo_shapes.displayed and self.floor_shapes_file:
            sh.display_list([self.fcontours.sh, self.fareas.sh])
        sh.display_list([self.floor.sh])

        if self.SAKURA_GPU_PERFORMANCE == 'low':
            if self.display_shadows:
                sh.display_list([self.sh_shadows])
            sh.display_list([self.trajs.sh])
        else:
            if self.display_shadows:
                if self.cube.height > 0.01:
                    sh.display_list([self.sh_back_shadows])
                sh.display_list([self.sh_shadows])
            sh.display_list([self.sh_back_trajects])

        sh.display_list([self.cube.sh, self.lines.sh])

    def send_new_dates(self, th_value = None):
        if len(self.cube.proj_corners_bottom):
            times = [   {'time': self.data.mins[0],
                            'x': self.cube.proj_corners_bottom[0][0],
                            'y': self.cube.proj_corners_bottom[0][1]},
                        {'time': self.data.maxs[0],
                            'x': self.cube.proj_corners_up[0][0],
                            'y': self.cube.proj_corners_up[0][1]},
                        {'time': float(self.data.curr_date),
                            'x': self.cube.proj_curr_pt[0],
                            'y': self.cube.proj_curr_pt[1]} ]
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

        msg = [{'action': 'none'}]
        if state == UP: #leaving any interaction modes
            ndate = time.time()
            #if self.imode == 'double-click':
            #    self.unselect_trajects(self.selected_trajects)
            #    self.idate = ndate
            #    msg = [{'action': 'unselectall'}]
            #elif self.selection_activated:
            if self.selection_activated:
                if ndate - self.idate < 0.15:
                    self.hovered_target = self.hovered_trajectory()
                    if self.hovered_target != -1 :
                        name = self.data.trajects_names[self.hovered_target]
                        if not self.hovered_target in self.selected_trajects:
                            self.select_trajects([self.hovered_target])
                            msg = [{'action': 'select', 'id': self.hovered_target, 'name': name}]
                        else:
                            self.unselect_trajects([self.hovered_target])
                            msg = [{'action': 'unselect', 'id': self.hovered_target, 'name': name}]
            else:
                if ndate - self.idate < 0.15:
                    self.hovered_target = self.hovered_trajectory()
                    if self.hovered_target != -1:
                        name = self.data.trajects_names[self.hovered_target]
                        msg = [{'action': 'none', 'id': self.hovered_target, 'name': name}]

            self.cube.reset()
            self.imode = 'none'

        else: #STATE == DOWN
            if self.cube.current_edge == -1: #Not on an edge !!!
                if button == LEFT_BUTTON:
                    ndate = time.time()
                    # if ndate - self.idate < 0.2 and self.selection_activated:
                    #         self.imode = 'double-click'
                    # else:
                    self.imode = 'rotation'

                    self.idate = time.time()
                elif button == RIGHT_BUTTON:
                    self.imode = 'translation'
                    self.idate = time.time()
            else:   #On an edge !!!!
                if button == LEFT_BUTTON:
                    self.imode = 'scale'
                    self.idate = time.time()
                elif button == RIGHT_BUTTON:
                    self.imode = self.cube.crop_mode(self.mouse)
                    self.idate = time.time()
        return msg

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
        self.compute_proj_cube_corners()
        self.send_new_dates()

    def reset_zoom(self):
        dir = gm.vector(self.projo.position, self.projo.viewpoint)
        diff = self.projo.init_zoom - gm.norm(dir)
        self.on_wheel(diff*10)

    def reset_cube_height(self):
        print('reset_cube_height')
        self.cube.height = 1

    def reset_projo_position(self):
        self.projo.reset_position()
        self.compute_proj_cube_corners()

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
        elif key == b'F':
            self.floor.set_updatable_height(not self.floor.updatable_height)
        elif key == b'q':
            self.toggle_density(not self.data.display_density)
        elif int(key) in range(0,10):
            if not int(key) in self.selected_trajects:
                self.select_trajects([int(key)])
            else:
                self.unselect_trajects([int(key)])
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

    def set_floor_shape_file(self, fname, init):
        if self.debug:
            print('\t\33[1;32mReading floor shape...\33[m', end='')
        self.geo_shapes.reset()
        self.floor_shapes_file = fname
        r = self.geo_shapes.read_shapes(fname)
        if self.debug:
            if r: print('\tOk')
        if not init:
            self.update_geo_shapes()
            self.update_floor()

    def set_updatable_floor(self, updatable=None):
        print('updatable', updatable)
        if updatable != None:
            self.floor.set_updatable_height(updatable)
        else:
            self.floor.set_updatable_height(not self.floor.updatable_height)

    def set_back_color(self, c):
        self.back_color = c

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

    def select_trajects(self, l):
        for i in l:
            if i >= 0 and i < len(self.data.trajects):
                if i not in self.selected_trajects:
                    self.new_selections.append(i)
            else:
                print('\t\33[1;31mTrajectory index out of range !!!\33[m')

    def unselect_trajects(self, l):
        for i in l:
            if i >= 0 and i < len(self.data.trajects):
                if i in self.selected_trajects:
                    self.new_selections.append(i)
            else:
                print('\t\33[1;31mTrajectory index out of range !!!\33[m')

    def select_trajects_by_name(self, names):
        res = []
        for n in names:
            traj, id = self.data.traject_from_name(n)
            if id == None:
                res.append({'name': n, 'answer': 'unkown trajectory'})
            else:
                if id not in self.selected_trajects:
                    self.new_selections.append(id)
                    res.append({'name': n, 'answer': 'selected'})
                else:
                    res.append({'name': n, 'answer': 'already selected'})
        return res

    def unselect_trajects_by_name(self, names):
        res = []
        for n in names:
            traj, id = self.data.traject_from_name(n)
            if id == None:
                res.append({'name': n, 'answer': 'unkown trajectory'})
            else:
                if id in self.selected_trajects:
                    self.new_selections.append(id)
                    res.append({'name': n, 'answer': 'unselected'})
                else:
                    res.append({'name': n, 'answer': 'already unselected'})

    def unselect_all_trajects(self):
        self.unselect_trajects(self.selected_trajects)

    def toggle_shadows(self, b):
        self.display_shadows = b

    def hide_trajectories(self, names):
        res = []
        if len(names):
            for n in names:
                traj, id = self.data.traject_from_name(n)
                if id == None:
                    res.append({'name': n, 'answer': 'unknown trajectory'})
                elif id in self.data.displayed:
                    index = self.data.displayed.index(id)
                    self.data.displayed.pop(index)
                    res.append({'name': n, 'answer': 'hidden'})
                else:
                    res.append({'name': n, 'answer': 'already hidden'})
            self.trajs.geometry(self.data)
            self.data.make_meta()
            self.trajs.update_arrays()
            self.update_cube_and_lines()

        return res

    def show_trajectories(self, names):
        res = []
        if len(names):
            for n in names:
                traj, id = self.data.traject_from_name(n)
                if id == None:
                    res.append({'name': n, 'answer': 'unknown trajectory'})
                elif id not in self.data.displayed:
                    res.append({'name': n, 'answer': 'shown'})
                    self.data.displayed.append(id)
                else:
                    res.append({'name': n, 'answer': 'already shown'})
            self.data.displayed.sort()
            self.trajs.geometry(self.data)
            self.data.make_meta()
            self.trajs.update_arrays()
            self.update_cube_and_lines()

        return res

    def get_shapes(self):
        return self.geo_shapes.get_shapes_info()

    def highlight_shapes(self, l):
        self.geo_shapes.highlight_shapes(l)
        self.fareas.geometry(self.data, self.geo_shapes)
        self.fareas.update_arrays()

    def toggle_density(self, b):
        self.data.toggle_density(b)
        self.trajs.geometry(self.data)
        self.trajs.update_arrays()

    def set_trajects_width(self, v):
        self.trajects_width = v

    def read_density(self, b):
        self.data.read_density(b)

    def toggle_selection(self, b):
        self.selection_activated = b
