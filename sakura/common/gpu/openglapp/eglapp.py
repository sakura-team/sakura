from sakura.common.gpu import libegl
from sakura.common.gpu.openglapp.base import OpenglAppBase

class EGLApp(OpenglAppBase):

    def __init__ (self, handler):
        OpenglAppBase.__init__(self, handler)
        self.ctx = libegl.EGLContext()

    def trigger_local_display(self):
        pass    # EGL is headless

    def window_resize(self, w, h):
        self.ctx.resize(w, h)

    def prepare_display(self):
        pass

    def make_current(self):
        self.ctx.make_current()

    def release_display(self):
        pass

    def init(self, w=None, h=None):
        if w:   self.width = w
        if h:   self.height = h

        self.ctx.initialize(self.width, self.height)
        self.ctx.make_current()

        self.handler.init()

    def loop(self):
        raise Exception('EGL-based OpenglApp cannot be run standalone.')
