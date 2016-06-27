#!/usr/bin/env python
import rpyc
from utils import *
from rpyc.utils.server import ThreadedServer
from PantedaData import ServerPantedaDataOperator

DEBUG = False

class PantedaService(rpyc.Service):
    def __init__(self, *args, **kwargs):
        rpyc.Service.__init__(self, *args, **kwargs)
        self.next_op_id = 0
        self.operators = {}
        self.register_operator_classes()
    def register_operator_classes(self):
        self.operator_classes = {
            cls.OP_TYPE : cls  \
                for cls in SERVER_OPERATOR_CLASSES
        }
    def exposed_register_operator(self, op_type):
        op_id = self.next_op_id
        self.next_op_id += 1
        op_class = self.operator_classes[op_type]
        operator = op_class()
        self.operators[op_id] = operator
        return op_id
    def exposed_set_operator_sources(self, op_id, source_op_ids):
        operator = self.operators[op_id]
        source_ops = [self.operators[i] for i in source_op_ids]
        operator.set_source_ops(source_ops)
    def exposed_get_operator_iterator(self, op_id):
        operator = self.operators[op_id]
        return operator.get_iterator()
    def exposed_get_operator_output_len(self, op_id):
        operator = self.operators[op_id]
        return operator.get_output_len()
    def exposed_get_operator_output(self, op_id, i):
        operator = self.operators[op_id]
        return operator.get_result(i)
    def exposed_describe_outputs(self, op_id):
        operator = self.operators[op_id]
        return tuple([
                tuple([
                    (col_label, 'enum')
                        if isinstance(col_type, AutoEnum)
                    else (col_label, col_type)
                for col_label, col_type in output])
            for output in operator.describe_outputs()])
    def exposed_describe_enum(self, op_id, out_id, name):
        operator = self.operators[op_id]
        for col_name, col_type in operator.describe_outputs()[out_id]:
            if col_name == name:
                return tuple(col_type.iterkeys())


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

class ServerPantedaSelectOperator(ServerPantedaStepByStepOperator):
    OP_TYPE = "OWPantedaSelect"
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


if __name__ == "__main__":
    SERVER_OPERATOR_CLASSES = [
        ServerPantedaMeanOperator,
        ServerPantedaSelectOperator,
        ServerPantedaDataOperator
    ]
    server = ThreadedServer(PantedaService, port = 12345)
    server.start()

