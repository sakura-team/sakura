import numpy as np
import OpenGL.GL as gl
from PIL import Image

PPM_HEADER = """\
P6
%(width)s %(height)s
255
"""

def write_ppm(filename, width, height):
    img_buf = gl.glReadPixels(0, 0, width, height, gl.GL_RGB, gl.GL_UNSIGNED_BYTE)
    # GL_RGB => 3 components per pixel
    img = np.frombuffer(img_buf, np.uint8).reshape(height, width, 3)[::-1]
    bin_data = img.tobytes('C')
    header = PPM_HEADER % dict(
        width = width,
        height = height
    )
    with open(filename, "wb") as f:
        f.write(header.encode('ASCII'))
        f.write(bin_data)

class JPEGWriter:
    def __init__(self):
        self.array, self.array_size = None, 0
    def __call__(self, f, width, height, **params):
        # TODO: check how we could reuse the previous buffer, if (width, height)
        # does not change. Maybe by creating the Image object first and providing
        # its buffer to glReadPixels.
        args = (0, 0, width, height, gl.GL_RGB, gl.GL_UNSIGNED_BYTE)
        array = gl.glReadPixels(*args)
        im = Image.frombuffer('RGB', (width, height), array, "raw", 'RGB', 0, -1)
        im.save(f, 'JPEG', **params)

write_jpg = JPEGWriter()
