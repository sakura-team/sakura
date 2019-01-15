import os, enum

class MouseMoveReporting(enum.Enum):
    NONE                    = 0
    LEFT_CLICKED            = 1
    RIGHT_CLICKED           = 2
    LEFT_OR_RIGHT_CLICKED   = 3
    ALWAYS                  = 4

if os.environ.get('SAKURA_ENV', 'undef') == 'daemon':
    SAKURA_DISPLAY_STREAMING = True
else:
    SAKURA_DISPLAY_STREAMING = False

# GPU backend might be specified by SAKURA_GPU_BACKEND env variable
backend = os.environ.get('SAKURA_GPU_BACKEND', 'undef')
if backend not in ('egl', 'glut', 'undef'):
    print('WARNING: SAKURA_GPU_BACKEND env variable has unknown value: ' + backend)
    backend = 'undef'

if backend == 'undef':
    # SAKURA_GPU_BACKEND undefined, guess it
    if os.environ.get('SAKURA_ENV', 'undef') == 'daemon':
        # OpenGLApp will be used in regular sakura environment
        # (an operator run by a daemon)
        backend = 'egl'
    else:
        # OpenGLApp will be run standalone (for debugging)
        backend = 'glut'

if backend == 'egl':
    from sakura.common.gpu.openglapp.eglapp import EGLApp as OpenglApp
else: # backend == 'glut'
    from sakura.common.gpu.openglapp.glutapp import GlutApp as OpenglApp
