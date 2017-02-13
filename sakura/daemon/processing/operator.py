import inspect, os.path
from sakura.daemon.processing.table import InputTable, OutputTable
from sakura.daemon.processing.tab import Tab
from sakura.daemon.processing.tools import Registry

class Operator(Registry):
    def __init__(self, op_id):
        self.op_id = op_id
        self.input_tables = []
        self.output_tables = []
        self.parameters = []
        self.tabs = []
    def register_input(self, input_table_label):
        return self.register(self.input_tables, InputTable, input_table_label)
    def register_output(self, output_table_label, compute_cb, internal=False):
        return self.register(self.output_tables, OutputTable, self, output_table_label, compute_cb, internal)
    def register_parameter(self, param_label, cls):
        return self.register(self.parameters, cls, param_label)
    def register_tab(self, tab_label, js_path):
        return self.register(self.tabs, Tab, tab_label, js_path)
    def is_ready(self):
        for table in self.input_tables:
            if not table.connected():
                return False
        for parameter in self.parameters:
            if not parameter.selected():
                return False
        return True
    def descriptor(op_cls):
        return op_cls.NAME, op_cls.SHORT_DESC, op_cls.TAGS, op_cls.ICON
    def get_info_serializable(self):
        return dict(
            op_id = self.op_id,
            cls_name = self.NAME,
            parameters = [ param.get_info_serializable() for param in self.parameters ],
            inputs = [ table.get_info_serializable() for table in self.input_tables ],
            outputs = [ table.get_info_serializable() for table in self.output_tables ],
            tabs = [ tab.get_info_serializable() for tab in self.tabs ]
        )
    def get_file_content(self, file_path):
        operator_py_path = inspect.getabsfile(self.__class__)
        op_root_path = os.path.split(operator_py_path)[0]
        abs_file_path = os.path.join(op_root_path, file_path)
        with open(abs_file_path) as f:
            return f.read()
    def auto_fill_parameters(self):
        for param in self.parameters:
            param.auto_fill()

class InternalOperator(Operator):
    def __init__(self):
        # internal operators do not need to record an operator id,
        # let's call the base constructor with 0
        super().__init__(0)
