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
        sources = []
        for ds in datasets.load():
            if hasattr(ds, 'SOURCE'):
                # statically defined source
                source = ds.SOURCE
            else:
                # dynamically generated source
                try:
                    source = ds.load_source(self)
                except BaseException as exc:
                    print('WARNING: could not load dataset %s: %s. IGNORED.' % \
                            (ds.__name__, str(exc).strip()))
                    continue
            sources.append(source)
        for source in sorted(sources, key=lambda s: s.label):
            self.register_output(source=source)
        # no parameters
        pass
