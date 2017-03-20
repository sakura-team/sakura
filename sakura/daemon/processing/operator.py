import inspect
from pathlib import Path
from sakura.common.tools import SimpleAttrContainer
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
        operator_py_path = Path(inspect.getabsfile(self.__class__))
        self.root_dir = operator_py_path.parent
    def register_input(self, input_stream_label):
        return self.register(self.input_streams, InputStream, input_stream_label)
    def register_output(self, output_stream_label, compute_cb):
        return self.register(self.output_streams, OutputStream, self, output_stream_label, compute_cb)
    def register_internal_stream(self, internal_stream_label, compute_cb):
        return self.register(self.internal_streams, InternalStream, self, internal_stream_label, compute_cb)
    def register_parameter(self, param_label, cls):
        return self.register(self.parameters, cls, param_label)
    def register_tab(self, tab_label, html_path):
        return self.register(self.tabs, Tab, tab_label, html_path)
    def is_ready(self):
        for stream in self.input_streams:
            if not stream.connected():
                return False
        for parameter in self.parameters:
            if not parameter.selected():
                return False
        return True
    def descriptor(op_cls):
        return SimpleAttrContainer(
                name = op_cls.NAME,
                short_desc = op_cls.SHORT_DESC,
                tags = op_cls.TAGS,
                icon = op_cls.ICON)
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
    def auto_fill_parameters(self):
        for param in self.parameters:
            param.auto_fill()
    def serve_file(self, request):
        print('serving ' + request.filepath, end="")
        resp = request.serve(str(self.root_dir))
        print(' ->', resp)
        return resp
    def get_file_content(self, file_path):
        with (self.root_dir / file_path).open() as f:
            return f.read()
    def get_file_tree(self, path=None):
        if path == None:
            path = self.root_dir
        return tuple(self.iterate_file_tree(path))
    def iterate_file_tree(self, p):
        for f in p.iterdir():
            if f.is_dir():
                yield dict(
                    name = f.name,
                    is_dir = True,
                    dir_entries = self.get_file_tree(f)
                )
            else:
                yield dict(
                    name = f.name,
                    is_dir = False
                )
    def save_file_content(self, file_path, file_content):
        with (self.root_dir / file_path).open('w') as f:
            f.write(file_content)

    def new_file(self, file_path, file_content):
        self.save_file_content(file_path, file_content)

    def new_directory(self, dir_path):
        (self.root_dir / dir_path).mkdir()

    def move_file(self, file_src, file_dst):
        (self.root_dir / file_src).rename(
                    self.root_dir / file_dst)

    def delete_file(self, path):
        self.delete_abs_file(self.root_dir / path)

    def delete_abs_file(self, p):
        if p.is_dir():
            for f in p.iterdir():
                self.delete_abs_file(f)
            p.rmdir()
        else:
            p.unlink()

class InternalOperator(Operator):
    def __init__(self):
        # internal operators do not need to record an operator id,
        # let's call the base constructor with 0
        super().__init__(0)
