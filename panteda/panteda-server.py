#!/usr/bin/env python
import rpyc, sys
from utils import *
from rpyc.utils.server import ThreadedServer
from bottle import Bottle
from PantedaData import ServerPantedaDataOperator
from PantedaMean import ServerPantedaMeanOperator
from PantedaSelect import ServerPantedaSelectOperator

DEBUG = False

class PantedaService(object):
    def __init__(self, *args, **kwargs):
        self.next_op_id = 0
        self.operators = {}
        self.register_operator_classes()
    def register_operator_classes(self):
        self.operator_classes = {
            cls.OP_TYPE : cls  \
                for cls in SERVER_OPERATOR_CLASSES
        }
    def register_operator(self, op_type):
        op_id = self.next_op_id
        self.next_op_id += 1
        op_class = self.operator_classes[op_type]
        operator = op_class()
        self.operators[op_id] = operator
        print 'registered operator ' + op_type
        return op_id
    def set_operator_sources(self, op_id, source_op_ids):
        operator = self.operators[op_id]
        source_ops = [self.operators[i] for i in source_op_ids]
        operator.set_source_ops(source_ops)
    def get_operator_iterator(self, op_id):
        operator = self.operators[op_id]
        return operator.get_iterator()
    def get_operator_output_len(self, op_id):
        operator = self.operators[op_id]
        return operator.get_output_len()
    def get_operator_output(self, op_id, i):
        operator = self.operators[op_id]
        return operator.get_result(i)
    def describe_outputs(self, op_id):
        operator = self.operators[op_id]
        return tuple([
                tuple([
                    (col_label, 'enum')
                        if isinstance(col_type, AutoEnum)
                    else (col_label, col_type)
                for col_label, col_type in output])
            for output in operator.describe_outputs()])
    def describe_enum(self, op_id, out_id, name):
        operator = self.operators[op_id]
        for col_name, col_type in operator.describe_outputs()[out_id]:
            if col_name == name:
                return tuple(col_type.iterkeys())

class RPyCPantedaService(PantedaService, rpyc.Service):
    def __init__(self, *args, **kwargs):
        rpyc.Service.__init__(self, *args, **kwargs)
        PantedaService.__init__(self, *args, **kwargs)
        self.exposed_register_operator = self.register_operator
        self.exposed_set_operator_sources = self.set_operator_sources
        self.exposed_get_operator_iterator = self.get_operator_iterator
        self.exposed_get_operator_output_len = self.get_operator_output_len
        self.exposed_get_operator_output = self.get_operator_output
        self.exposed_describe_outputs = self.describe_outputs
        self.exposed_describe_enum = self.describe_enum

class BottlePantedaService(PantedaService):
    def serve(self):
        app = Bottle()

        @app.route('/operator/register/<op_type>')
        def register_operator(op_type):
            return { 'op_id': self.register_operator(op_type) }

        app.run()


if __name__ == "__main__":
    SERVER_OPERATOR_CLASSES = [
        ServerPantedaMeanOperator,
        ServerPantedaSelectOperator,
        ServerPantedaDataOperator
    ]
    if len(sys.argv) > 1 and sys.argv[1] == '--rpyc':
        server = ThreadedServer(RPyCPantedaService, port = 12345)
        server.start()
    else:
        service = BottlePantedaService()
        service.serve()

