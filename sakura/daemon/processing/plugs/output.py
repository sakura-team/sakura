from sakura.daemon.processing.plugs.base import PlugBase

class OutputPlug(PlugBase):
    def __init__(self, operator, label=None, source=None, condition=None, explain_disabled = None):
        super().__init__()
        self._label = label
        self._source = source
        self._condition = condition
        self._explain_disabled = explain_disabled
        self.on_change.subscribe(lambda: operator.notify_output_plug_change(self))
    @property
    def source(self):
        return self._source
    @source.setter
    def source(self, val):
        if val != self._source:
            self._source = val
            self.on_change.notify()
    @property
    def enabled(self):
        if self._condition is not None and not self._condition():
            return False
        return self._source is not None
    @property
    def disabled_message(self):
        if self.enabled:
            raise AttributeError
        if self._explain_disabled is None:
            return 'The operator could not publish output data yet.'
        else:
            return self._explain_disabled()
    def pack(self):
        # caution, the label may be the default value 'Output',
        # or a label provided as an __init__() parameter of this
        # plug object, or the source label when available.
        # That's why the info dict is built with 3 steps below.
        info = dict(
                label = 'Output',
                **self.pack_status_info())
        if self._label is not None:
            info.update(label = self._label)
        if self.enabled:
            info.update(**self.source.pack())
        return info
