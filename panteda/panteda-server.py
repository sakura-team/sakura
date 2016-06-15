#!/usr/bin/env python
import rpyc
from rpyc.utils.server import ThreadedServer

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

class ServerPantedaIterator(object):
    def __init__(self, srv_op):
        self.srv_op = srv_op
        self.i = 0
    def next(self):
        res = self.srv_op.get_result(self.i)
        if res == None:
            raise StopIteration
        self.i += 1
        return res

class ServerPantedaStepByStepOperator(object):
    def __init__(self):
        self.source_ops = None
    def set_source_ops(self, source_ops):
        self.source_ops = source_ops
    def __iter__(self):
        return self.get_iterator()
    def get_iterator(self):
        return ServerPantedaIterator(self)

class ServerPantedaOneStepOperator(ServerPantedaStepByStepOperator):
    def __init__(self):
        self.result = None
    def get_result(self, i):
        if self.result == None:
            self.result = self.compute()
        if i < len(self.result):
            return self.result[i]
        else:
            return None

class ServerPantedaMeanOperator(ServerPantedaOneStepOperator):
    OP_TYPE = "OWPantedaMean"
    def compute(self):
        source_op = self.source_ops[0]
        res = 0
        num = 0
        for record in source_op:
            res += record[0]
            num += 1
        return [ [ float(res)/num ] ]

class ServerPantedaSelectOperator(ServerPantedaStepByStepOperator):
    OP_TYPE = "OWPantedaSelect"
    def get_result(self, i):
        source_op = self.source_ops[0]
        record = source_op.get_result(i)
        if record == None:
            return None
        else:
            return [record[1]]

class ServerPantedaDataOperator(ServerPantedaStepByStepOperator):
    OP_TYPE = "OWPantedaData"
    DATA = [[0, 1, 2], [4, 7, 5], [12, 0, 3]]
    def get_result(self, i):
        if i < len(ServerPantedaDataOperator.DATA):
            return ServerPantedaDataOperator.DATA[i]
        else:
            return None

if __name__ == "__main__":
    SERVER_OPERATOR_CLASSES = [
        ServerPantedaMeanOperator,
        ServerPantedaSelectOperator,
        ServerPantedaDataOperator
    ]
    server = ThreadedServer(PantedaService, port = 12345)
    server.start()

