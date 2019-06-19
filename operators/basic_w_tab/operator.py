#!/usr/bin/env python
from sakura.daemon.processing.operator import Operator
from sakura.daemon.processing.parameter import NumericColumnSelection
from sakura.daemon.processing.source import ComputedSource

class basic_w_tab(Operator):
    NAME = "Basic-w-Tab"
    SHORT_DESC = "Basic operator, with an additional tab"
    TAGS = [ "visualisation, tutorial"]

    def construct(self):
        # additional tab
        self.register_tab('Additional Tab', 'basic_w_tab.html')

        # inputs
        self.input = self.register_input('Input data')


        # output
        output_source = ComputedSource('Output data', self.compute)
        output_source.add_column('Value', float)
        self.register_output(
                label = 'Output data',
                source = output_source)

        self.value_to_add = 0

    def compute(self):
        yield (self.value_to_add, )

    def handle_event(self, ev_type, **info):
        if ev_type == 'add':
            self.value_to_add += 10
