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

    def download_tile(self, lon, lat, z):
        # cache directory
        if not os.path.isdir("./tiles_cache/"):
            print("\33[1;32m\tCreating tiles folder...\33[m", end='')
            os.makedirs("./tiles_cache/")
            print("Ok (tiles_cache)")

        x, y = tn.tileXY(lat, lon, z)

        # tile file
        fdir    = "./tiles_cache/" + self.layer + "/" + str(z) + "/"
        fname   = fdir + str(x) + "_" + str(y) + ".pytile"

        if not os.path.exists(fname):
            url = tn.tileURL(x, y, z, self.layer)
            self.img = Image.open(requests.get(url, stream=True).raw).convert('RGB').transpose(Image.FLIP_TOP_BOTTOM)
            if not os.path.isdir(fdir):
                os.makedirs(fdir)

            o = open(fname, 'wb')
            pickle.dump(self.img, o)
            o.close()
        else:
            o = open(fname, 'rb')
            self.img = pickle.load(o)
            o.close()

        return tn.tileEdges(x,y,z)
