import platform as pl, gevent, time
from sakura.common.gpu.openglapp.base import OpenglAppBase

try:
    from OpenGL.GL      import *
    from OpenGL.GLU     import *
    from OpenGL.GL      import shaders
    import OpenGL.GLUT    as glut
except:
    print ('''ERROR: PyOpenGL not installed properly. ** ''')

# do not try to exceed this number of frame per seconds.
# if we reach it, let other greenlets work.
FPS_LIMITATION = 60

class GlutApp(OpenglAppBase):

    def trigger_local_display(self):
        glut.glutPostRedisplay()

    def window_resize(self, w, h):
        glut.glutReshapeWindow(w, h)

    def make_current(self):
        pass    # FIX THIS

    def prepare_display(self):
        pass

    def release_display(self):
        glut.glutSwapBuffers()

    def init(self, w=None, h=None):
        if w:   self.width = w
        if h:   self.height = h

        try:
            glut.glutInit()
        except Exception as e:
            print(e)
            sys.exit()

        if pl.system() == 'Darwin': #Darwin: OSX
            glut.glutInitDisplayString('double rgba samples=8 core depth')
        else:   #Other: Linux
            try:
                glut.glutInitDisplayMode(
                        glut.GLUT_DOUBLE | \
                        glut.GLUT_RGBA | \
                        glut.GLUT_MULTISAMPLE | \
                        glut.GLUT_DEPTH)
            except Exception as e:
                print('Issue detected')
                print(e)
                sys.exit()
        glut.glutInitWindowSize (self.width, self.height)
        glut.glutCreateWindow (self.label)

        self.handler.init()

        glut.glutDisplayFunc(self.display)
        glut.glutKeyboardFunc(self.on_key_press)
        glut.glutMouseFunc(self.on_mouse_click)
        glut.glutMotionFunc(self.on_mouse_motion)
        glut.glutPassiveMotionFunc(self.on_mouse_motion)
        glut.glutReshapeFunc(self.on_resize)

        self.last_glut_idle_time = time.time()
        glut.glutIdleFunc(self.on_glut_idle)
        if self.currently_streamed:
            # sakura core defines the main program loop,
            # so we have to run GLUT's own loop in another
            # greenlet.
            self.spawn_greenlet_loop()

    def on_glut_idle(self):
        # This method allows to make glut gevent-friendly, by allowing
        # other greenlets to run when idle.
        # call gevent.sleep taking into account the framerate
        nt = time.time()
        dt = 1/FPS_LIMITATION - (nt - self.last_glut_idle_time)
        self.last_glut_idle_time = nt
        if  dt > 0:
            gevent.sleep(dt)
        else:   # we are late
            gevent.idle()

    def spawn_greenlet_loop(self):
        g_task = gevent.Greenlet.spawn(self.loop)
        self.greenlets.append(g_task)

    def loop(self):
        glut.glutMainLoop()
