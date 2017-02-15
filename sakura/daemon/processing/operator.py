import inspect, os.path
from sakura.daemon.processing.stream import InputStream, OutputStream, InternalStream
from sakura.daemon.processing.tab import Tab
from sakura.daemon.processing.tools import Registry

class Operator(Registry):
    def __init__(self, op_id):
        self.op_id = op_id
        self.input_streams = []
        self.output_streams = []
        self.internal_streams = []
        self.parameters = []
        self.tabs = []
        operator_py_path = inspect.getabsfile(self.__class__)
        self.op_root_path = os.path.split(operator_py_path)[0]
    def register_input(self, input_stream_label):
        return self.register(self.input_streams, InputStream, input_stream_label)
    def register_output(self, output_stream_label, compute_cb):
        return self.register(self.output_streams, OutputStream, self, output_stream_label, compute_cb)
    def register_internal_stream(self, internal_stream_label, compute_cb):
        return self.register(self.internal_streams, InternalStream, self, internal_stream_label, compute_cb)
    def register_parameter(self, param_label, cls):
        return self.register(self.parameters, cls, param_label)
    def register_tab(self, tab_label, js_path):
        return self.register(self.tabs, Tab, tab_label, js_path)
    def is_ready(self):
        for stream in self.input_streams:
            if not stream.connected():
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
            inputs = [ stream.get_info_serializable() for stream in self.input_streams ],
            outputs = [ stream.get_info_serializable() for stream in self.output_streams ],
            internal_streams = [ stream.get_info_serializable() for stream in self.internal_streams ],
            tabs = [ tab.get_info_serializable() for tab in self.tabs ]
        )
    def get_abs_file_path(self, file_path):
        return os.path.join(self.op_root_path, file_path)
    def get_file_content(self, file_path):
        with open(self.get_abs_file_path(file_path)) as f:
            return f.read()
    def auto_fill_parameters(self):
        for param in self.parameters:
            param.auto_fill()
    def serve_file(self, request):
        print('serving ' + request.filepath, end="")
        resp = request.serve(self.op_root_path)
        print(' ->', resp)
        return resp

class InternalOperator(Operator):
    def __init__(self):
        # internal operators do not need to record an operator id,
        # let's call the base constructor with 0
        super().__init__(0)
