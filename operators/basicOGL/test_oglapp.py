#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from sakura.common.gpu.openglapp import OpenglApp
from hellocube.hellocube import HelloCube

oapp = OpenglApp(HelloCube())
oapp.init(800, 600)
oapp.loop()
