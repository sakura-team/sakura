import platform as pl
from sakura.common.gpu.openglapp.base import OpenglAppBase

try:
    from OpenGL.GL      import *
    from OpenGL.GLU     import *
    from OpenGL.GL      import shaders
    import OpenGL.GLUT    as glut
except:
    print ('''ERROR: PyOpenGL not installed properly. ** ''')

class GlutApp(OpenglAppBase):

    def notify_change(self):
        glut.glutPostRedisplay()

    def window_resize(self, w, h):
        glut.glutReshapeWindow(w, h)

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
        glut.glutCreateWindow ('Basic OGL')

        self.handler.init()

        glut.glutDisplayFunc(self.display)
        glut.glutKeyboardFunc(self.on_key_press)
        glut.glutMouseFunc(self.on_mouse_click)
        glut.glutMotionFunc(self.on_mouse_motion)
        glut.glutReshapeFunc(self.on_resize)

    def loop(self):
        glut.glutMainLoop()
