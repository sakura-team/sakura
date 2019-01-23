from sakura.daemon.processing.source import ComputedSource

class OutputPlug:
    def __init__(self, label=None, source=None):
        self._label = label
        self._source = source
    @property
    def source(self):
        if self._source is None:
            # not_ready, return a fake source.
            # the GUI should be updated to read the "ready" flag.
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
    def is_ready(self):
        return self._source is not None
    def pack(self):
        info = dict(ready = self.is_ready(), label = 'Output')
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
