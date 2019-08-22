#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import  sys, gevent, time
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

    def print_help(self):
        print()
        print('usage: stc_ws.py -data csv_path [-h] [-help] [-server] [-color path]\n \
                [-shape path] [-performance string] [-shadows bool] [-verbose]')
        print()
        print("  h, help\t: print this help")
        print("  data\t\t: csv file path (mandatory)")
        print("  server\t: server mode activation")
        print("  color\t\t: color file path (random colors if option not defined)")
        print("  shape\t\t: shape file path (no shapes if option not defined)")
        print("  performance\t: high (default), low")
        print("  shadows\t: yes (default), no")
        print("  verbose\t: display some activaty infos in prompt")
        print()

    def __init__(self):

        if len(sys.argv) < 2 or sys.argv[1] in ('-h', '-help'):
            self.print_help()
            sys.exit()

        self.stc = SpaceTimeCube()
        self.stc.debug = True
        self.stc.app = self
        self.server_mode = False

        if '-data' in sys.argv:
            ind = sys.argv.index('-data')
            self.data_file = sys.argv[ind+1]

        if '-server' in sys.argv:
            self.server_mode = True

        if '-color' in sys.argv:
            ind = sys.argv.index('-color')
            self.stc.set_colors_file(sys.argv[ind+1])

        if '-shape' in sys.argv:
            ind = sys.argv.index('-shape')
            self.stc.set_floor_shape_file(sys.argv[ind+1])

        if '-shadows' in sys.argv:
            ind = sys.argv.index('-shadows')
            if sys.argv[ind+1] != 'yes':
                self.stc.toggle_shadows(False)

        if '-verbose' in sys.argv:
            self.stc.verbose = True

        if '-performance' in sys.argv:
            ind = sys.argv.index('-performance')
            self.stc.SAKURA_GPU_PERFORMANCE = sys.argv[ind+1]
        else:
            self.stc.SAKURA_GPU_PERFORMANCE = 'high'


    def init(self):
        glutInit(sys.argv)
        if pl.system() == 'Darwin':
            glutInitDisplayString('double stencil rgba samples=8 core depth')
        else:
            try:
                glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_MULTISAMPLE | GLUT_DEPTH | GLUT_STENCIL)
            except Exception as e:
                print('Issue detected')
                print(e)
                sys.exit()

        glutInitWindowSize (400, 300)
        glutCreateWindow ('Space-Time Cube, by Michael Ortega, LIG')

        self.stc.on_resize(400, 300)
        self.stc.init()
        self.stc.clean_data()
        self.stc.load_data(file = self.data_file)
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
        if not self.server_mode:
            glutPostRedisplay()

    def keyboard(self, key, x, y):
        if key == b'\x1b':
            if self.server_mode:
                self.stc_server._stop()
        self.stc.on_key_press(key, x, y)
        if not self.server_mode:
            glutPostRedisplay()

    def mclick(self, button, state, x, y):
        res = self.stc.on_mouse_click(button, state, x, y)
        if not self.server_mode:
            glutPostRedisplay()
        return res

    def mmotion(self, x, y):
        self.stc.on_mouse_motion(x, y)
        if not self.server_mode:
            glutPostRedisplay()

    def idle(self):
        if self.server_mode:
            gevent.idle()
            glutPostRedisplay()

    def mpassive(self, x, y):
        self.mmotion(x, y)
        if not self.server_mode:
            glutPostRedisplay()

    ################------------------------------------------------------------
    ### server funcs
    def stc_test(self, a):
        print(a)

    def set_wiggle(self, value= None):
        self.stc.toggle_wiggle(value)
        glutPostRedisplay()

    def stc_image(self, imageQ):
        if self.stc.is_wiggle_on():
            self.stc.animation()
        buf = BytesIO()
        if imageQ == 'very_low':
            self.image_to_send.save(buf, format= 'JPEG', quality= 20)
        elif imageQ == 'low':
            self.image_to_send.save(buf, format= 'JPEG', quality= 50)
        else:
            self.image_to_send.save(buf, format= 'JPEG', quality= 100)
        return buf.getvalue()

    def stc_dates(self):
        return self.stc.send_new_dates()

    def stc_resize(self, w, h):
        glutReshapeWindow(w,h)
        self.reshape(w, h)

    def init_server(self, p):
        self.stc_server = STC_server = ws_server(port = p)
        self.stc_server.start({ \
                    'test':                 self.stc_test,
                    'image':                self.stc_image,
                    'move':                 self.mmotion,
                    'click':                self.mclick,
                    'wheel':                self.stc.on_wheel,
                    'reset_zoom':           self.stc.reset_zoom,
                    'reset_position':       self.stc.reset_projo_position,
                    'get_trajectories':     self.stc.get_trajectories,
                    'hide_trajectories':    self.stc.hide_trajectories,
                    'show_trajectories':    self.stc.show_trajectories,
                    'get_semantic_names':   self.stc.get_semantic_names,
                    'select_semantic':      self.stc.select_colored_semantic,
                    'darkness':             self.stc.set_floor_darkness,
                    'wiggle':               self.set_wiggle,
                    'dates':                self.stc_dates,
                    'resize':               self.stc_resize,
                    'set_updatable_floor':  self.stc.set_updatable_floor,
                    'reset_cube_height':    self.stc.reset_cube_height,
                    'get_shapes':           self.stc.get_shapes,
                    'highlight_shapes':     self.stc.highlight_shapes
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
