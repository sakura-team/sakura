import inspect
from pathlib import Path
from sakura.common.io import pack
from sakura.daemon.processing.stream import InputStream
from sakura.daemon.processing.tab import Tab
from sakura.daemon.processing.parameter import ParameterException
from gevent.lock import Semaphore

class Operator:
    IGNORED_FILENAMES = ("__pycache__", ".DS_Store")
    def __init__(self, op_id):
        self.op_id = op_id
        operator_py_path = Path(inspect.getabsfile(self.__class__))
        self.root_dir = operator_py_path.parent
        self.event_lock = Semaphore()
    # overridable dynamic properties
    @property
    def input_streams(self):
        return getattr(self, '_input_streams', ())
    @property
    def output_streams(self):
        return getattr(self, '_output_streams', ())
    @property
    def internal_streams(self):
        return getattr(self, '_internal_streams', ())
    @property
    def parameters(self):
        return getattr(self, '_parameters', ())
    @property
    def tabs(self):
        return getattr(self, '_tabs', ())
    # static properties
    def register_input(self, input_stream_label):
        return self.register('_input_streams', InputStream(input_stream_label))
    def register_output(self, output):
        return self.register('_output_streams', output)
    def register_internal_stream(self, internal_stream):
        return self.register('_internal_streams', internal_stream)
    def register_parameter(self, param):
        return self.register('_parameters', param)
    def register_tab(self, tab_label, html_path):
        return self.register('_tabs', Tab(tab_label, html_path))
    # other functions
    def register(self, container_name, obj):
        container = getattr(self, container_name, [])
        container.append(obj)
        setattr(self, container_name, container)
        return obj
    def is_ready(self):
        for stream in self.input_streams:
            if not stream.connected():
                return False
        for parameter in self.parameters:
            if not parameter.selected():
                return False
        return True
    def descriptor(op_cls):
        return dict(
                name = op_cls.NAME,
                short_desc = op_cls.SHORT_DESC,
                tags = op_cls.TAGS,
                icon = op_cls.ICON)
    def get_num_parameters(self):
        return len(self.parameters)
    def pack(self):
        return pack(dict(
            op_id = self.op_id,
            cls_name = self.NAME,
            parameters = self.parameters,
            inputs = self.input_streams,
            outputs = self.output_streams,
            internal_streams = self.internal_streams,
            tabs = self.tabs
        ))
    def auto_fill_parameters(self, permissive = False, stream = None):
        if permissive:
            ignored_exception = ParameterException
        else:
            ignored_exception = ()  # do not ignore any exception
        for param in self.parameters:
            # restrict to parameters concerning the specified stream if any
            if stream != None and not param.is_linked_to_stream(stream):
                continue
            try:
                param.auto_fill()
            except ignored_exception:
                pass
    def unselect_parameters(self, stream = None):
        for param in self.parameters:
            # restrict to parameters concerning the specified stream if any
            if stream != None and not param.is_linked_to_stream(stream):
                continue
            param.unset_value()
    def serve_file(self, request):
        return request.serve(str(self.root_dir))
    def get_file_content(self, file_path):
        with (self.root_dir / file_path).open() as f:
            return f.read()
    def get_file_tree(self, path=None):
        if path == None:
            path = self.root_dir
        return tuple(self.iterate_file_tree(path))
    def iterate_file_tree(self, p):
        for f in p.iterdir():
            if f.name in Operator.IGNORED_FILENAMES:
                continue
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
    def sync_handle_event(self, event):
        # operators handle events one at a time
        # (easier for the operator developer)
        with self.event_lock:
            return self.handle_event(event)
