from sakura.common.tools import ObservableEvent, StatusMixin
from sakura.common.errors import APIRequestError

class PlugBase(StatusMixin):
    def __init__(self):
        self.on_change = ObservableEvent()
    @property
    def source(self):
        raise NotImplementedError   # implement in subclasses
    @property
    def enabled(self):
        raise NotImplementedError   # implement in subclasses
    @property
    def disabled_message(self):
        raise NotImplementedError   # implement in subclasses
    def verify_enabled(self):
        if not self.enabled:
            raise APIRequestError(self.disabled_message)
    def get_range(self, *args, **kwargs):
        self.verify_enabled()
        return self.source.get_range(*args, **kwargs)
    def __iter__(self):
        self.verify_enabled()
        return self.source.__iter__()
    def get_columns_info(self):
        self.verify_enabled()
        return self.source.get_columns_info()
