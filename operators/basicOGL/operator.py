#!/usr/bin/env python
from sakura.daemon.processing.operator import Operator
from sakura.daemon.processing.parameter import NumericColumnSelection
from sakura.daemon.processing.source import ComputedSource

from time import time
import numpy as np
import subprocess
import os
from .hellocube import hellocube as hcube

class basicOGL(Operator):
    NAME = "Basic OpenGL"
    SHORT_DESC = "Basic OpenGL operator, with a simple cube that one can rotate with left mouse button"
    TAGS = [ "visualisation"]
    def construct(self):
        # additional tabs
        self.register_tab('OGL', 'basicOGL.html?op_id='+str(self.op_id))
        self.button_state = 1
        self.bOGL = hcube.hellocube()
        self.bOGL.start()

    def handle_event(self, ev_type, **info):
        if ev_type == 'init':
            url = "/streams/%d/video.mjpeg" % self.op_id
            return { "mjpeg_url": url }
        elif ev_type == 'resize':
            return self.bOGL.resize(info['w'], info['h'])
        elif ev_type == 'mouse_clicks':
            self.button_state = info['state']
            return self.bOGL.mouse_clicks(info['button'], info['state'], info['x'], info['y'])
        elif ev_type == 'mouse_motion':
            if self.button_state == 0:
                return self.bOGL.mouse_motion(info['x'], info['y'])

    def stream_jpeg_frames(self):
        yield from self.bOGL.stream_jpeg_frames()
