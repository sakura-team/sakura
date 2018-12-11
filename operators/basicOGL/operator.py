#!/usr/bin/env python
from sakura.daemon.processing.operator import Operator
from sakura.daemon.processing.parameter import NumericColumnSelection
from sakura.daemon.processing.source import ComputedSource

from time import time
import numpy as np
import subprocess
import os
from .hellocube import hellocube as hcube

class basicOGL(Operator):
    NAME = "Basic OpenGL"
    SHORT_DESC = "Basic OpenGL operator, with a simple cube that one can rotate with left mouse button"
    TAGS = [ "visualisation"]
    def construct(self):
        # additional tabs
        self.register_tab('OGL', 'basicOGL.html')
        self.bOGL = hcube.hellocube(800, 600)
        self.bOGL.start()

    def handle_event(self, ev_type, **info):
        print('#################')
        print(ev_type, info)
