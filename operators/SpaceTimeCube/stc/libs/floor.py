#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#Michael ORTEGA - 07/April/2017

import time, datetime, PIL, requests
import  numpy as np
from    PIL import Image
from . import geomaths as gm
from . import mercator as mrc
from . import tilenames   as  tn

class floor:
    def __init__(self):
        self.width = 100
        self.height = 100
        self.img = Image.new('RGB', (self.width,self.height), (255, 255, 255))

    def download_tile(self, lon, lat, z):
        x, y = tn.tileXY(lat, lon, z)
        url = tn.tileURL(x, y, z, 'OpenStreetMap')
        self.img = Image.open(requests.get(url, stream=True).raw).convert('RGB').transpose(Image.FLIP_TOP_BOTTOM)
        return tn.tileEdges(x,y,z)

        '''
        if not os.path.isdir("./tiles_cache/"):
            print("Creating tiles_cache folder")
            os.makedirs("./tiles_cache/")

        info = current_tile['url_info']
        fdir    =   "./tiles_cache/" +info['type']        +"/"+ \
                                str(info['depth'])  +"/"+ \
                                str(info['x'])      +"/"
        fname   = fdir + str(info['y']) + '.pytile'
        if not os.path.exists(fname):
            url = tn.tileURL(   info['x'],
                                info['y'],
                                info['depth'],
                                info['type'])

            current_tile['img'] = Image.open(requests.get(url, stream=True).raw)
            if not os.path.isdir(fdir):
                os.makedirs(fdir)

            o = open(fname, 'wb')
            pickle.dump(current_tile['img'], o)
            o.close()
        else:
            o = open(fname, 'rb')
            current_tile['img'] = pickle.load(o)
            o.close()

        current_tile['status'] = 'done'
        '''
