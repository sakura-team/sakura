#!/usr/bin/env python
from sakura.daemon.processing.operator import Operator

class CodeOperator(Operator):
    NAME = "Code"
    SHORT_DESC = "Fake operator for testing code editor integration."
    TAGS = [ "test", "code" ]
    def construct(self):
        # additional tabs
        self.register_tab('Code-proto', 'code.html')
        self.register_tab('API-test', 'testtab.html')
