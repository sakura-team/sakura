from sakura.common.tools import ObservableEvent, StatusMixin
from sakura.common.errors import APIRequestError

class PlugBase(StatusMixin):
    def __init__(self):
        self.on_change = ObservableEvent()
    def get_label(self):
        return self.pack()['label']
    def get_length(self):
        return self.pack().get('length', None)
    def stream_csv(self, gzip_compression=False):
        if not self.enabled:
            raise APIRequestError('Operator plug is not enabled yet.')
        yield from self.source.stream_csv(gzip_compression)
    def pack(self):
        raise NotImplementedError   # implement in subclasses
    @property
    def source(self):
        raise NotImplementedError   # implement in subclasses
    @property
    def enabled(self):
        raise NotImplementedError   # implement in subclasses
    @property
    def disabled_message(self):
        raise NotImplementedError   # implement in subclasses
    def get_source(self):
        return self.source
    def verify_enabled(self):
        if not self.enabled:
            raise APIRequestError(self.disabled_message)
    def get_range(self, *args, **kwargs):
        self.verify_enabled()
        return self.source.get_range(*args, **kwargs)
    def chunks(self, *args, **kwargs):
        self.verify_enabled()
        return self.source.chunks(*args, **kwargs)
    def __iter__(self):
        self.verify_enabled()
        return self.source.__iter__()
    def get_columns_info(self):
        self.verify_enabled()
        return self.source.get_columns_info()
