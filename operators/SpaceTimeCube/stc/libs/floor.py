#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#Michael ORTEGA - 07/April/2017

import time, datetime, PIL, requests, os, pickle
import  numpy as np
from    PIL import Image
from . import geomaths as gm
from . import mercator as mrc
from . import tilenames   as  tn

class floor:
    def __init__(self):
        self.layer = 'OpenStreetMap'
        self.width = 100
        self.height = 100
        self.img = Image.new('RGB', (self.width,self.height), (255, 255, 255))

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
