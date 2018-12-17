#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from sakura.common.gpu.openglapp import OpenglApp
from hellocube import hellocube as hcube

oapp = OpenglApp(hcube.hellocube())
oapp.init(800, 600)
oapp.loop()
