#!/usr/bin/env python
from sakura.daemon.processing.operator import Operator
from sakura.common.gpu.openglapp import OpenglApp
from .stc.spacetimecube import SpaceTimeCube
from sakura.common.gpu.openglapp import MouseMoveReporting


class spacetimecubeOperator(Operator):
    NAME = "Space-Time Cube"
    SHORT_DESC = "Displays GPS trajectories, with time as a vertical component"
    TAGS = [ "visualisation"]
    def construct(self):
        self.planned_task = False
        # inputs
        self.input_plug = self.register_input('GPS data')
        # parameters
        self.id_column_param = self.register_parameter(
                'TAG_BASED_COLUMN_SELECTION', 'Trajectory id', self.input_plug, 'id')
        self.dat_column_param = self.register_parameter(
                'TAG_BASED_COLUMN_SELECTION', 'Dates', self.input_plug, 'date')
        self.lng_column_param = self.register_parameter(
                'TAG_BASED_COLUMN_SELECTION', 'Longitude', self.input_plug, 'longitude')
        self.lat_column_param = self.register_parameter(
                'TAG_BASED_COLUMN_SELECTION', 'Latitude', self.input_plug, 'latitude')
        self.ele_column_param = self.register_parameter(
                'TAG_BASED_COLUMN_SELECTION', 'Elevation', self.input_plug, 'elevation')
        # additional tab
        self.register_tab('STC', 'spacetimecube.html')
        # opengl app
        self.ogl_app = OpenglApp(SpaceTimeCube(self.root_dir))
        self.ogl_app.mouse_move_reporting = getattr(self.ogl_app.handler,
                                                    "mouse_move_reporting",
                                                    MouseMoveReporting.ALWAYS)
        self.ogl_app.handler.debug = True
        self.register_opengl_app(self.ogl_app)

    def init_op_data(self):
        # Cleaning data first
        self.ogl_app.handler.clean_data()

        # Sending new data now
        src = self.input_plug.source
        cols = src.select(  self.id_column_param.column,
                            self.dat_column_param.column,
                            self.lng_column_param.column,
                            self.lat_column_param.column,
                            self.ele_column_param.column)
        self.ogl_app.push_event('loading_data_start')
        for ch in cols.chunks():
            self.ogl_app.handler.load_data(chunk=ch)
            self.ogl_app.notify_change()
        self.ogl_app.push_event('loading_data_end')
        self.ogl_app.handler.update_floor()

    def handle_event(self, ev_type, **info):
        if ev_type == 'onload':
            self.init_op_data()
            return self.ogl_app.handler.get_trajectories()
            self.ogl_app.notify_change()

        elif ev_type == 'wiggle':
            #TODO: implement a 'unplan' periodic task
            self.ogl_app.handler.toggle_wiggle(info['value'])
            if not self.planned_task and info['value']:
                self.planned_task = True
                self.ogl_app.plan_periodic_task(self.ogl_app.handler.animation, 1/25.)

        elif ev_type == 'floor_darkness':
            self.ogl_app.handler.set_floor_darkness(info['value'])
            self.ogl_app.notify_change()

        elif ev_type == 'cube_height':
            self.ogl_app.handler.set_cube_height(info['value'])
            self.ogl_app.notify_change()

        elif ev_type == 'show_trajectories':
            self.ogl_app.handler.show_trajectories(info['value'])
            self.ogl_app.notify_change()

        elif ev_type == 'hide_trajectories':
            self.ogl_app.handler.hide_trajectories(info['value'])
            self.ogl_app.notify_change()

        elif ev_type == 'get_map_layers':
            return self.ogl_app.handler.get_map_layers()
            self.ogl_app.notify_change()

        elif ev_type == 'set_map_layer':
            return self.ogl_app.handler.set_map_layer(info['value'])
            self.ogl_app.notify_change()

        else:
            print('\33[1;31m!!!Unknown Event', ev_type, '!!!\33[m')
