import OpenGL.EGL as egl

class SurfaceBase:
    def __init__(self, egl_dpy, egl_config, *subclass_args):
        self.egl_dpy, self.egl_config = egl_dpy, egl_config
        self.egl_surface = None
        self.subclass_init(*subclass_args)
    def initialize(self, width, height):
        self.egl_surface = self.subclass_create_egl_surface(width, height)
        return self.egl_surface is not None
    def release(self):
        if self.is_current():
            # make not current
            egl.eglMakeCurrent(self.egl_dpy, egl.EGL_NO_SURFACE, egl.EGL_NO_SURFACE, egl.EGL_NO_CONTEXT)
        if self.egl_surface is not None:
            egl.eglDestroySurface(self.egl_dpy, self.egl_surface)
        self.subclass_release()
    def is_current(self):
        if self.egl_surface is None:
            return False
        curr_surface = egl.eglGetCurrentSurface(egl.EGL_DRAW)
        if not curr_surface:
            return False
        return curr_surface.address == self.egl_surface.address
    def make_current(self, egl_context):
        if self.is_current():
            return  # nothing to do
        res = egl.eglMakeCurrent(self.egl_dpy, self.egl_surface, self.egl_surface, egl_context)
        return res
    def resize(self, egl_context, width, height):
        is_current = self.is_current()
        self.release()
        self.initialize(width, height)
        if is_current:
            self.make_current(egl_context)
    def subclass_init(self, *subclass_args):
        raise NotImplementedError   # should be implemented in subclass
    def subclass_create_egl_surface(self, width, height):
        raise NotImplementedError   # should be implemented in subclass
    def subclass_release(self):
        raise NotImplementedError   # should be implemented in subclass
