from sakura.daemon.processing.source import ComputedSource
from sakura.common.tools import ObservableEvent, StatusMixin

class OutputPlug(StatusMixin):
    def __init__(self, label=None, source=None):
        self._label = label
        self._source = source
        self.on_change = ObservableEvent()
    @property
    def source(self):
        if self._source is None:
            # not_ready, return a fake source.
            # the GUI should be updated to read the "enabled" flag.
            print('note: fake output source returned (not ready)')
            output_source = ComputedSource('Fake output',
                lambda: (yield ('output is not ready!',))
            )
            output_source.add_column('ERROR', str)
            output_source.length = 1
            return output_source
        return self._source
    @source.setter
    def source(self, val):
        self._source = val
        self.on_change.notify()
    @property
    def enabled(self):
        return self._source is not None
    @property
    def disabled_message(self):
        if self.enabled:
            raise AttributeError
        return 'The operator could not publish output data yet.'
    def pack(self):
        # caution, the label may be the default value 'Output',
        # or the source label if provided, or a label provided
        # as an __init__() parameter of this plug object.
        # That's why the info dict is built with 3 steps below.
        info = dict(
                label = 'Output',
                **self.pack_status_info())
        info.update(**self.source.pack())
        if self._label is not None:
            info.update(label = self._label)
        return info
    def get_range(self, *args, **kwargs):
        return self.source.get_range(*args, **kwargs)
    def __iter__(self):
        return self.source.__iter__()
    def get_columns_info(self):
        return self.source.get_columns_info()
