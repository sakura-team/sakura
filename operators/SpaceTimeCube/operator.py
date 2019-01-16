#!/usr/bin/env python
from sakura.daemon.processing.operator import Operator
from sakura.common.gpu.openglapp import OpenglApp
from .stc.spacetimecube import SpaceTimeCube

class spacetimecubeOperator(Operator):
    NAME = "Space-Time Cube"
    SHORT_DESC = "Displays GPS trajectories, with time as a vertical component"
    TAGS = [ "visualisation"]
    def construct(self):
        # additional tab
        self.register_tab('STC', 'spacetimecube.html')
        # opengl app
        ogl_app = OpenglApp(SpaceTimeCube())
        ogl_app.plan_periodic_task(ogl_app.handler.animation, .01)
        self.register_opengl_app(ogl_app)
