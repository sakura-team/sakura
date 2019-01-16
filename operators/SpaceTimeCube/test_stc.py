#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from sakura.common.gpu.openglapp import OpenglApp
from stc.spacetimecube import SpaceTimeCube

oapp = OpenglApp(SpaceTimeCube())
oapp.init(800, 600)
oapp.plan_periodic_task(oapp.handler.animation, .01)
oapp.loop()
