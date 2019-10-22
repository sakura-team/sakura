#!/usr/bin/env python
from sakura.daemon.processing.operator import Operator
from sakura.daemon.processing.source import ComputedSource
from numpy.lib import recfunctions

from time import time
import numpy as np

class colsselection(Operator):
    NAME = "Columns Selection"
    SHORT_DESC = "Select columns from a table."
    TAGS = ["filter"]

    def construct(self):
        # inputs
        self.input = self.register_input('Input table')

        # additional tabs
        self.register_tab('Select', 'colsselection.html')

    def handle_event(self, ev_type):
        return {}
