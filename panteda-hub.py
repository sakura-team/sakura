#!/usr/bin/env python
import rpyc, bottle, sys, os
from utils import *
from rpyc.utils.server import ThreadedServer
from bottle import Bottle
from PantedaData import ServerPantedaDataOperator
from PantedaMean import ServerPantedaMeanOperator
from PantedaSelect import ServerPantedaSelectOperator

DEBUG = False
CURDIR = os.path.dirname(os.path.abspath(__file__))

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
    def set_operator_source(self, op_id, in_id, source_op_id):
        operator = self.operators[op_id]
        source_op = self.operators[source_op_id]
        operator.set_source_op(in_id, source_op)
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
    def __init__(self, webapp_dir):
        PantedaService.__init__(self)
        self.webapp_path = CURDIR + '/' + webapp_dir
        self.iterators = []

    def serve(self):
        app = Bottle()

        @app.route('/operator/register/<op_type>')
        def register_operator(op_type):
            return { 'op_id': self.register_operator(op_type) }

        @app.route('/operator/<op_id:int>/outputs')
        def describe_outputs(op_id):
            return { 'desc': self.describe_outputs(op_id) }

        @app.route('/link/<op_src_id:int>/<out_id:int>/to/<op_dst_id:int>/<in_id:int>')
        def link(op_src_id, out_id, op_dst_id, in_id):
            self.set_operator_source(op_dst_id, in_id, op_src_id)
            return { }

        @app.route('/operator/<op_id:int>/output/<out_id:int>/<col_label>/desc')
        def describe_enum(op_id, out_id, enum_label):
            return { 'desc': self.describe_enum(op_id, out_id, col_label) }

        @app.route('/operator/<op_id:int>/result/<out_id:int>/row/<row_id:int>')
        def get_operator_result_row(op_id, out_id, row_id):
            return { 'row': self.get_operator_output(op_id, row_id) }

        @app.route('/operator/<op_id:int>/result/<out_id:int>/len')
        def get_operator_result_len(op_id, out_id):
            return { 'len': self.get_operator_output_len(op_id) }

        @app.route('/operator/<op_id:int>/iterate')
        def get_operator_iterator(op_id):
            iterator = self.get_operator_iterator(op_id)
            iterator_id = len(self.iterators)
            self.iterators.append(iterator)
            return { 'it_id': iterator_id }

        @app.route('/iterator/<it_id:int>/next')
        def iterator_next(it_id):
            try:
                return { 'row': self.iterators[it_id].next() }
            except StopIteration:
                return { }

        # if no route was found above, look for static files in webapp subdir
        @app.route('/')
        @app.route('/<filepath:path>')
        def server_static(filepath = 'index.html'):
            return bottle.static_file(filepath, root = self.webapp_path)

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
        if len(sys.argv) == 1:
            webapp_dir = 'basic_webapp'
        else:
            webapp_dir = sys.argv[1]
        service = BottlePantedaService(webapp_dir)
        service.serve()

