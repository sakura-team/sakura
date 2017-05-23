#!/usr/bin/env python
from sakura.daemon.processing.operator import Operator
from . import datasets

class DataSampleOperator(Operator):
    NAME = "Data Sample"
    SHORT_DESC = "Data Sample."
    TAGS = [ "testing", "datasource" ]

    def construct(self):
        # no inputs
        pass
        # outputs:
        for ds in datasets.load():
            self.register_output(ds.STREAM)
        # no parameters
        pass
