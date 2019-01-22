#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#Michael ORTEGA - 07/April/2017

import time, datetime, PIL
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
