#!/usr/bin/env python
from sakura.daemon.processing.operator import Operator
from sakura.common.gpu.openglapp import OpenglApp
from .hellocube.hellocube import HelloCube

class basicOGL(Operator):
    NAME = "Basic OpenGL"
    SHORT_DESC = "Basic OpenGL operator, with a simple cube that one can rotate with left mouse button"
    TAGS = [ "visualisation"]
    def construct(self):
        # additional tab
        self.register_tab('OGL', 'basic-ogl.html')
        # opengl app
        ogl_app = OpenglApp(HelloCube(self.root_dir))
        self.register_opengl_app(ogl_app)
