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
            output = self.register_output(ds.NAME, ds.COMPUTE_CALLBACK)
            if hasattr(ds, 'LENGTH'):
                output.length = ds.LENGTH
            for col_info in ds.COLUMNS:
                output.add_column(*col_info)
        # no parameters
        pass
