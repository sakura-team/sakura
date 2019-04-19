#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#Michael ORTEGA - 07/April/2017

import time, datetime, PIL, requests, os, pickle, sys
import  numpy as np
from    PIL import Image
from .. import geomaths     as gm
from .. import mercator     as mc
from .. import tilenames    as tn
from .. import shader       as sh

try:
    from OpenGL.GL      import *
    from OpenGL.GL      import shaders
except:
    print ('''ERROR in cube.py: PyOpenGL not installed properly. ** ''')

class floor:
    def __init__(self):
        self.layer      = 'OpenStreetMap'
        self.width      = 100
        self.height     = 100
        self.darkness   = .5
        self.img = Image.new('RGB', (self.width,self.height), (255, 255, 255))

        self.vertices       = np.array([[0, 0, 0], [0, 0, 1], [1, 0, 1],
                                            [0, 0, 0], [1, 0, 1], [1, 0, 0]])
        self.text_coords    = np.array([ [0.,0.], [0.,1.], [1.,1.],
                                            [0.,0.], [1.,1.], [1.,0.]])
        self.sh             = sh.shader()
        self.sh.display     = self.display
        #self.sh.update_texture  = self.u_texture

    def generate_buffers_and_attributes(self):
        self.vbo_vertices       = glGenBuffers(1)
        self.vbo_text_coords    = glGenBuffers(1)
        self.sh.texture_id      = glGenTextures(1)
        self.attr_vertices      = sh.new_attribute_index()
        self.attr_text_coords   = sh.new_attribute_index()

    def update_arrays(self):
        sh.bind(self.vbo_vertices, self.vertices, self.attr_vertices, 3, GL_FLOAT)
        sh.bind(self.vbo_text_coords, self.text_coords, self.attr_text_coords, 2, GL_FLOAT)

    def display(self):
        self.update_uniforms(self.sh)
        glDrawArrays(GL_TRIANGLES, 0, len(self.vertices))

    def update_texture(self, init = False):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.sh.texture_id);

        w = self.img.width
        h = self.img.height

        black = Image.new('RGB', (w, h), (0, 0, 0))
        f = self.img.resize((w, h), Image.ANTIALIAS)
        final = Image.blend(f, black, self.darkness)

        arr = np.fromstring(final.tobytes(), np.uint8)
        glTexImage2D(   GL_TEXTURE_2D, 0, GL_RGB,
                        final.width,
                        final.height,
                        0, GL_RGB, GL_UNSIGNED_BYTE, arr);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);

    def create_shader(self, dir, glsl_version):
        return sh.create(   dir+'/floor.vert',
                            None,
                            dir+'/floor.frag',
                            [self.attr_vertices, self.attr_text_coords],
                            ['in_vertex', 'in_text_coords'],
                            glsl_version)

    def download_tile(self, x, y, z, img_x, img_y):
        # cache directory
        if not os.path.isdir("./tiles_cache/"):
            os.makedirs("./tiles_cache/")

        # tile file
        fdir    = "./tiles_cache/" + self.layer + "/" + str(z) + "/"
        fname   = fdir + str(x) + "_" + str(y) + ".pytile"

        img = None
        if not os.path.exists(fname):
            url = tn.tileURL(x, y, z, self.layer)
            img = Image.open(requests.get(url, stream=True).raw).convert('RGB').transpose(Image.FLIP_TOP_BOTTOM)
            if not os.path.isdir(fdir):
                os.makedirs(fdir)

            o = open(fname, 'wb')
            pickle.dump(img, o)
            o.close()
        else:
            o = open(fname, 'rb')
            img = pickle.load(o)
            o.close()
        self.img.paste(img, box= (img_x*256, img_y*256))

    def get_layers(self):
        return tn.layers_names()

    def set_darkness(self, value):
        if value > 1.0:     self.darkness = 1.0
        elif value < 0.0:   self.darkness = 0.0
        else:               self.darkness = value
        self.update_texture()

    def download_tile_with_perc(self, coords, z, perc, debug = False):
        self.download_tile( coords['lon'],
                            coords['lat'],
                            z,
                            coords['img_x'],
                            coords['img_y'])
        if debug:
            print(  '\r\t\t\33[1;32mDownloading tiles '+perc+'%\33[m',
                    end='',
                    flush = True)

    def update(self, mins, maxs, debug = False):
        if debug:
            print('\t\33[1;32mUpdating floor...\33[m', flush = True)
        sys.stdout.flush()

        # longitude and latitude of the cube corners
        lon_min, lat_min = mc.lonlat_from_mercator( mins[1],mins[2])
        lon_max, lat_max = mc.lonlat_from_mercator( maxs[1],maxs[2])

        # computing the higher depth that gives a tile smaller than the cube size
        z = tn.depth_from_size(lon_max - lon_min)+1

        # coordinates of the tiles
        lon_t_min, lat_t_min = tn.tileXY(lat_min, lon_min, z)
        lon_t_max, lat_t_max = tn.tileXY(lat_max, lon_max, z)

        edges = []
        coords = []
        size = [lon_t_max - lon_t_min + 1, lat_t_min - lat_t_max + 1]
        for lo in range(size[0]):
            for la in range(size[1]):
                lon = lon_t_min + lo
                lat = lat_t_min - la
                edges.append(tn.tileEdges(lon, lat , z))
                coords.append({'lon': lon, 'lat': lat, 'img_x': lo, 'img_y': la })

        self.img = self.img.resize(((size[0])*256, (size[1])*256) )
        lon_min, lat_min = mc.mercator(edges[0]['w'], edges[0]['s'])
        lon_max, lat_max = mc.mercator(edges[-1]['e'], edges[-1]['n'])
        self.vertices = np.array([  [lon_min, 0, lat_min],
                                    [lon_min, 0, lat_max],
                                    [lon_max, 0, lat_max],
                                    [lon_min, 0, lat_min],
                                    [lon_max, 0, lat_max],
                                    [lon_max, 0, lat_min]])
        if debug:
            print('\t\t\33[1;32mDownloading tiles 0%\33[m', end='', flush = True)

        for i in range(len(coords)):
            self.download_tile_with_perc(coords[i], z, str(int((i+1)*100/len(coords))), debug)
            self.update_arrays()
            self.update_texture()
        if debug:
            print('\tOk', flush = True)
