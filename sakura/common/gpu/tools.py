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
    def __call__(self, f, width, height):
        new_array_size = width * height * 3
        if new_array_size > self.array_size:
            self.array = (gl.GLubyte * new_array_size)()
            self.array_size = new_array_size
        gl.glReadPixels(0, 0, width, height, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, self.array)
        im = Image.frombuffer('RGB', (width, height), self.array, "raw", 'RGB', 0, -1)
        im.save(f, 'JPEG')

write_jpg = JPEGWriter()
