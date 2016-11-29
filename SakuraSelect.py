#!/usr/bin/env python
from utils import ServerSakuraStepByStepOperator
DEBUG = False

class ServerSakuraSelectOperator(ServerSakuraStepByStepOperator):
    OP_TYPE = "OWSakuraSelect"
    def describe_outputs(self):
        if DEBUG: ecrire("Select description")
        source_op = self.source_ops[0]
        return ((source_op.describe_outputs()[0][1],),)
    def get_output_len(self):
        if DEBUG: ecrire("Select len")
        return self.source_ops[0].get_output_len()
    def get_result(self, i):
        if DEBUG: ecrire("Select get_r")
        source_op = self.source_ops[0]
        record = source_op.get_result(i)
        if record == None:
            return None
        else:
            return (record[1],)

