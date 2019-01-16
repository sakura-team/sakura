#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from sakura.common.gpu.openglapp import OpenglApp
from stc.spacetimecube import SpaceTimeCube

if len(sys.argv) < 2:
    print('ERROR !! We need a csv file')
    sys.exit()

oapp = OpenglApp(SpaceTimeCube())
oapp.init(800, 600)
oapp.plan_periodic_task(oapp.handler.animation, .01)
oapp.handler.load_data(file=sys.argv[1])
oapp.loop()
