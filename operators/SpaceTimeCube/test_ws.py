#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import  sys, gevent
import  platform         as pl
from    gevent           import Greenlet
from    PIL              import Image
from    io               import BytesIO
from    stc.spacetimecube import SpaceTimeCube
from    stc.libs.server             import *
import  json

try:
    from OpenGL.GL      import *
    from OpenGL.GLU     import *
    from OpenGL.GLUT    import *
except:
    print ('''ERROR: PyOpenGL not installed properly.''')


class wsock:
    def __init__(self):

        if len(sys.argv) < 2:
            print("\33[1;31mERROR !! We need a csv file\33[m")
            sys.exit()

        self.stc = SpaceTimeCube()
        self.stc.debug = True
        self.stc.app = self
        self.server_mode = False
        if '-server' in sys.argv:
            self.server_mode = True

    def init(self):
        glutInit(sys.argv)
        if pl.system() == 'Darwin':
            glutInitDisplayString('double rgba samples=8 core depth')
        else:
            try:
                glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_MULTISAMPLE | GLUT_DEPTH)
            except Exception as e:
                print('Issue detected')
                print(e)
                sys.exit()

        glutInitWindowSize (800, 600)
        glutCreateWindow ('Space-Time Cube, by Michael Ortega, LIG')

        self.stc.on_resize(800, 600)
        self.stc.init()
        self.stc.clean_data()
        self.stc.load_data(file=sys.argv[1])
        self.stc.update_floor()

        glutDisplayFunc(self.display)
        glutReshapeFunc(self.reshape)
        glutKeyboardFunc(self.keyboard)
        glutMouseFunc(self.mclick)
        glutMotionFunc(self.mmotion)
        glutPassiveMotionFunc(self.mpassive)


    def push_event(self, evt, *args, **kwargs):
        pass

    def display(self):
        self.stc.display()
        if self.server_mode:
            #tests for sending image
            w = self.stc.width
            h = self.stc.height
            image = glReadPixels(   0, 0,
                                    w, h,
                                    GL_RGB, GL_UNSIGNED_BYTE)
            self.image_to_send = Image.frombuffer('RGB', (w, h), image, 'raw', 'RGB', 0, 1).transpose(Image.FLIP_TOP_BOTTOM)
        glutSwapBuffers()

    def reshape(self, w, h):
        self.stc.on_resize(w, h)
        glutPostRedisplay()

    def keyboard(self, key, x, y):
        if key == b'\x1b':
            if self.server_mode:
                self.stc_server._stop()
        self.stc.on_key_press(key, x, y)
        glutPostRedisplay()

    def mclick(self, button, state, x, y):
        self.stc.on_mouse_click(button, state, x, y)
        glutPostRedisplay()

    def mmotion(self, x, y):
        self.stc.on_mouse_motion(x, y)
        glutPostRedisplay()

    def idle(self):
        if self.server_mode:
            gevent.idle()
            glutPostRedisplay()

    def mpassive(self, x, y):
        self.mmotion(x, y)


    ################------------------------------------------------------------
    ### server funcs
    def stc_test(self, a):
        print(a)

    def stc_image(self):
        buf = BytesIO()
        self.image_to_send.save(buf, format= 'JPEG', quality= 90)
        return buf.getvalue()

    def init_server(self, p):
        self.stc_server = STC_server = ws_server(port = p)
        self.stc_server.start({ 'test': self.stc_test,
                                'image': self.stc_image,
                                'move': self.mmotion,
                                'click': self.mclick,
                                'wheel': self.stc.on_wheel,
                                'get_trajectories': self.stc.get_trajectories,
                                'hide_trajectories': self.stc.hide_trajectories,
                                'show_trajectories': self.stc.show_trajectories,
                                })

    def loop(self):
        if self.server_mode:
            glutIdleFunc(self.idle)
            g1 = Greenlet.spawn(self.init_server, 10433)
            g2 = Greenlet.spawn(glutMainLoop)
            gevent.joinall([g1, g2], count=1)
        else:
            glutMainLoop()

mainwin = wsock()
mainwin.init()
mainwin.loop()
