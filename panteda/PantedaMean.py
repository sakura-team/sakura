#!/usr/bin/env python
from utils import ServerPantedaOneStepOperator
DEBUG = False

class ServerPantedaMeanOperator(ServerPantedaOneStepOperator):
    OP_TYPE = "OWPantedaMean"
    def describe_outputs(self):
        if DEBUG: ecrire("Mean description")
        source_op = self.source_ops[0]
        source_label = source_op.describe_outputs()[0][0][0]
        return ((("Mean(%s)" % source_label, 'float'),),)
    def get_output_len(self):
        if DEBUG: ecrire("Mean len")
        return 1
    def compute(self):
        if DEBUG: ecrire("Mean compute")
        source_op = self.source_ops[0]
        res = 0
        num = 0
        for record in source_op:
            res += record[0]
            num += 1
        return ((float(res)/num,),)


