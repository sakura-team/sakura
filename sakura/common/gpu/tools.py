import numpy as np
import OpenGL.GL as gl
from PIL import Image
import struct

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

class BMPWriter(struct.Struct):
    def __init__(self):
        self.headers_struct = struct.Struct("<2sIHHIIIIHHIIIIII")
    def __call__(self, f, width, height):
        data_offset = 14 + 40
        row_padding_len = (4 - (width * 3)) % 4
        length = data_offset + height * (width * 3 + row_padding_len)
        headers = self.headers_struct.pack(
                b'BM', length, 0, 0, data_offset,
                40, width, height, 1, 24, 0, 0, 10000, 10000, 0, 0)
        f.write(headers)
        args = (0, 0, width, height, gl.GL_BGR, gl.GL_UNSIGNED_BYTE)
        array = gl.glReadPixels(*args)
        f.write(array)

write_bmp = BMPWriter()

class FrameWriter:
    def __init__(self, pixel_fmt):
        self.gl_px_fmt = {
            'BGR': gl.GL_BGR,
            'RGB': gl.GL_RGB
        }.get(pixel_fmt)
        if self.gl_px_fmt is None:
            raise Exception('Unknown pixel format for FrameWriter: ' + repr(pixel_fmt))
        self.arrays = {}
    def __call__(self, f, width, height):
        size = 3*width*height
        array = self.arrays.get(size)
        if array is None:
            array = bytearray(size)
            self.arrays[size] = array
        gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, 1)
        args = (0, 0, width, height, self.gl_px_fmt, gl.GL_UNSIGNED_BYTE, array)
        gl.glReadPixels(*args)
        f.write(array)

write_rgb_frame = FrameWriter('RGB')
