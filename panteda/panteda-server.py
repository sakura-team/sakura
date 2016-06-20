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

class AutoEnum(dict):
    __all_enums = []
    def __init__(self):
        self.__enum_id = len(AutoEnum.__all_enums)
        AutoEnum.__all_enums.append(self)
        self.__i__ = -1
    def __getattr__(self, name):
        if self.has_key(name):
            return dict.__getitem__(self, name)
        else:
            self.__i__ += 1
            dict.__setitem__(self, name, self.__i__)
            return self.__i__
    def __getitem__(self, name):
        return self.__getattr__(name)
    @staticmethod
    def get(enum_id):
        return AutoEnum.__all_enums__[enum_id]

class ServerPantedaIterator(object):
    def __init__(self, srv_op):
        self.srv_op = srv_op
        self.i = 0
    def next(self):
        res = self.srv_op.get_result(self.i)
        if res == None:
            raise StopIteration
        self.i += 1
        return tuple(res)

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
    def describe_outputs(self):
        source_op = self.source_ops[0]
        source_label = source_op.describe_outputs()[0][0][0]
        return ((("Mean(%s)" % source_label, 'float'),),)
    def get_output_len(self):
        return 1
    def compute(self):
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
        source_op = self.source_ops[0]
        return ((source_op.describe_outputs()[0][1],),)
    def get_output_len(self):
        return self.source_ops[0].get_output_len()
    def get_result(self, i):
        source_op = self.source_ops[0]
        record = source_op.get_result(i)
        if record == None:
            return None
        else:
            return (record[1],)

STATUS = AutoEnum()
DATA = (    (0, 1, 2, STATUS.OK),
            (4, 7, 5, STATUS.NOK),
            (12, 0, 3, STATUS.BOF),
            (13, 4, 4, STATUS.OK)
)
DATA_COLS = (   ('col1', 'int'),
                ('col2', 'int'),
                ('col3', 'int'),
                ('status', STATUS)
)

class ServerPantedaDataOperator(ServerPantedaStepByStepOperator):
    OP_TYPE = "OWPantedaData"
    def describe_outputs(self):
        return (DATA_COLS,)
    def get_output_len(self):
        return len(DATA)
    def get_result(self, i):
        if i < len(DATA):
            return DATA[i]
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

