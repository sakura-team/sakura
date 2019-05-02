import os, glob
from sakura.common.gpu import libgbm
from sakura.common.gpu.libegl.devices.base import SurfaceBase
import OpenGL.EGL as egl
from ctypes import pointer

class GBMSurface(SurfaceBase):
    def subclass_init(self, gbm_dev):
        self.gbm_dev = gbm_dev
        self.gbm_surf = None
    def subclass_create_egl_surface(self, width, height):
        gbm_format = egl.EGLint()
        if not egl.eglGetConfigAttrib(self.egl_dpy, self.egl_config,
                            egl.EGL_NATIVE_VISUAL_ID, pointer(gbm_format)):
            return None
        self.gbm_surf = libgbm.gbm_surface_create(
                                        self.gbm_dev,
                                        width, height,
                                        gbm_format,
                                        libgbm.GBM_BO_USE_RENDERING)
        if not self.gbm_surf:
            self.gbm_surf = None
            return None
        egl_surface = egl.eglCreateWindowSurface(
                self.egl_dpy, self.egl_config, self.gbm_surf, None)
        if not egl_surface:
            print('GBMSurface initialize FAILED')
            self.release()
            return None
        return egl_surface
    def subclass_release(self):
        if self.gbm_surf is not None:
            libgbm.gbm_surface_destroy(self.gbm_surf)

class GBMDevice:
    @staticmethod
    def probe():
        cards = sorted(glob.glob("/dev/dri/renderD*"))
        return [ GBMDevice(card) for card in cards ]
    def __init__(self, dev_path):
        self.dev_path = dev_path
        self.name = "GBM device " + dev_path
    def initialize(self):
        self.gbm_fd = os.open(self.dev_path, os.O_RDWR|os.O_CLOEXEC)
        if self.gbm_fd < 0:
            return False
        self.gbm_dev = libgbm.gbm_create_device(self.gbm_fd)
        if self.gbm_dev is None:
            os.close(self.gbm_fd)
            return False
        return True
    def release(self):
        libgbm.gbm_device_destroy(self.gbm_dev)
        os.close(self.gbm_fd)
    def compatible_surface_type(self):
        return egl.EGL_WINDOW_BIT
    def get_egl_display(self):
        return egl.eglGetDisplay(self.gbm_dev)
    def create_surface(self, egl_dpy, egl_config):
        return GBMSurface(egl_dpy, egl_config, self.gbm_dev)
