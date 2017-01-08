

from sakura.daemon.processing.table import InputTable, OutputTable
from sakura.daemon.processing.parameter import Parameter
from sakura.daemon.processing.tools import Registry

class Operator(Registry):
    def __init__(self):
        self.input_tables = []
        self.output_tables = []
        self.parameters = []
    def register_input(self, input_table_label):
        return self.register(self.input_tables, InputTable, input_table_label)
    def register_output(self, output_table_label, compute_cb):
        return self.register(self.output_tables, OutputTable, self, output_table_label, compute_cb)
    def register_parameter(self, param_label, cls):
        return self.register(self.parameters, cls, param_label)
    def is_ready(self):
        for table in self.input_tables:
            if not table.connected():
                return False
        for parameter in self.parameters:
            if not parameter.selected():
                return False
        return True
    def descriptor(op_cls):
        # instanciate an operator, to check its number of inputs/outputs
        op = op_cls()
        op.construct()
        return op_cls.NAME, op_cls.TAGS, op_cls.ICON, len(op.input_tables), len(op.output_tables)
    def get_info_serializable(self):
        return dict(
            cls_name = self.NAME,
            parameters = [ param.get_info_serializable() for param in self.parameters ],
            inputs = [ table.get_info_serializable() for table in self.input_tables ],
            outputs = [ table.get_info_serializable() for table in self.output_tables ]
        )

