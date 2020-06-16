from sakura.common.io import pack, ORIGIN_ID
from sakura.common.tools import ObservableEvent, MonitoredList
from sakura.daemon.processing.plugs.input import InputPlug
from sakura.daemon.processing.plugs.output import OutputPlug
from sakura.daemon.processing.tab import Tab
from sakura.daemon.processing.parameter import instanciate_parameter
from gevent.lock import Semaphore

class Operator:
    IGNORED_FILENAMES = ("__pycache__", ".DS_Store")
    def __init__(self, op_id, hub_event_recorder, op_dir):
        self.op_id = op_id
        self.root_dir = op_dir
        self.event_lock = Semaphore()
        self._last_sources_origins = (None, None)
        self.pending_move_check = False
        self.hub_event_recorder = hub_event_recorder
        self.input_plugs = MonitoredList()
        self.input_plugs.on_change.subscribe(lambda: self.push_event_to_hub('altered_set_of_inputs'))
        self.output_plugs = MonitoredList()
        self.output_plugs.on_change.subscribe(lambda: self.push_event_to_hub('altered_set_of_outputs'))
        self.parameters = MonitoredList()
        self.parameters.on_change.subscribe(lambda: self.push_event_to_hub('altered_set_of_parameters'))
        self.tabs = MonitoredList()
        self.tabs.on_change.subscribe(lambda: self.push_event_to_hub('altered_set_of_tabs'))
        self.opengl_apps = MonitoredList()
        self.opengl_apps.on_change.subscribe(lambda: self.push_event_to_hub('altered_set_of_opengl_apps'))
        self.check_mode = False
    def push_event_to_hub(self, evt, *args, **kwargs):
        if not self.check_mode:
            self.hub_event_recorder(evt, *args, **kwargs)
    def notify_input_plug_change(self, in_plug):
        if self.check_mode:
            return
        in_plug_id = self.input_plugs.index(in_plug)
        self.push_event_to_hub('altered_input', in_plug_id)
        # if input plug is required and it was disconnected, reset output plugs
        if in_plug.required and not in_plug.enabled:
            for out_plug in self.output_plugs:
                out_plug.source = None
        # send notification targetting the link mixin object on hub
        if in_plug.source is None:
            print(self.op_id, 'input_now_none')
            self.push_event_to_hub('input_now_none', in_plug_id)
        else:
            print(self.op_id, 'input_no_longer_none')
            self.push_event_to_hub('input_no_longer_none', in_plug_id)
    def notify_output_plug_change(self, out_plug):
        self.push_event_to_hub('altered_output', self.output_plugs.index(out_plug))
    def notify_parameter_change(self, param):
        self.push_event_to_hub('altered_parameter', self.parameters.index(param))
    @property
    def _sources_origins(self):
        inputs_origins, outputs_origins = (), ()
        for in_plug in self.input_plugs:
            if in_plug.enabled:
                inputs_origins += (in_plug.source.get_origin_id(),)
            else:
                inputs_origins += (None,)
        for out_plug in self.output_plugs:
            if out_plug.enabled:
                outputs_origins += (out_plug.source.get_origin_id(),)
            else:
                outputs_origins += (None,)
        return inputs_origins, outputs_origins
    def _trigger_env_affinity_update(self):
        return self._sources_origins != self._last_sources_origins
    # static properties
    def register_input(self, input_plug_label, required = True):
        return self.register(self.input_plugs,
                             InputPlug(self, input_plug_label, required = required))
    def register_output(self, *args, condition = None, **kwargs):
        if condition is None:
            condition = self.is_ready
        return self.register(self.output_plugs, OutputPlug(self, *args, condition = condition, **kwargs))
    def register_parameter(self, param_type, label, *args, **kwargs):
        param = instanciate_parameter(self, param_type, label, *args, **kwargs)
        return self.register(self.parameters, param)
    def register_tab(self, tab_label, html_path):
        return self.register(self.tabs, Tab(tab_label, html_path))
    def register_opengl_app(self, ogl_app):
        ogl_id = len(self.opengl_apps)
        url_pattern = '/streams/%d/opengl/%d/video-${width}x${height}.mp4' % (self.op_id, ogl_id)
        ogl_app.url_pattern = url_pattern
        ogl_app.init()
        return self.register(self.opengl_apps, ogl_app)
    # other functions
    def register(self, container, obj):
        container.append(obj)
        return obj
    def is_ready(self):
        for plug in self.input_plugs:
            if not plug.enabled:
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
            parameters = self.parameters,
            inputs = self.input_plugs,
            outputs = self.output_plugs,
            tabs = self.tabs,
            opengl_apps = tuple(app.label for app in self.opengl_apps)
        ))
    def auto_fill_parameters(self, plug = None):
        for param in self.parameters:
            # restrict to parameters concerning the specified plug if any
            if plug != None and not param.is_linked_to_plug(plug):
                continue
            param.recheck()
    def check_input_compatibility_parameters(self, plug):
        for param in self.parameters:
            if param.is_linked_to_plug(plug):
                if not param.check_input_compatible():
                    return False
        return True
    def unselect_parameters(self, plug = None):
        for param in self.parameters:
            # restrict to parameters concerning the specified plug if any
            if plug != None and not param.is_linked_to_plug(plug):
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
            # note: calling str() below is mandatory if exploring
            # the remote filesystem of a sandbox.
            direntry_name = str(f.name)
            if direntry_name in Operator.IGNORED_FILENAMES:
                continue
            if f.is_dir():
                yield dict(
                    name = direntry_name,
                    is_dir = True,
                    dir_entries = self.get_file_tree(f)
                )
            else:
                yield dict(
                    name = direntry_name,
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
    def sync_handle_event(self, *args, **kwargs):
        # operators handle events one at a time
        # (easier for the operator developer)
        with self.event_lock:
            return self.handle_event(*args, **kwargs)
    def set_check_mode(self, check_mode):
        self.check_mode = check_mode
    def env_affinity(self):
        self._last_sources_origins = self._sources_origins
        inputs_origins, outputs_origins = self._last_sources_origins
        affinity = 0
        # add 3 points per input source on this daemon
        affinity += 3 * sum(map(lambda x: x == ORIGIN_ID, inputs_origins))
        # add 1 point per output source on this daemon
        affinity += 1 * sum(map(lambda x: x == ORIGIN_ID, outputs_origins))
        return affinity
    def move(self):
        self.pending_move_check = True
    def pop_pending_move_check(self):
        if self.is_ready() and self.pending_move_check:
            self.pending_move_check = False     # clear for next request
            return True
        else:
            return False
