from sakura.common.errors import APIRequestErrorOfflineDaemon, APIRequestError
from sakura.daemon.processing.plugs.base import PlugBase

class InputPlug(PlugBase):
    def __init__(self, operator, label, required = True):
        super().__init__()
        self.label = label
        self.source_plug = None
        self.required = required
        self.operator = operator
        self.on_change.subscribe(self.notify_to_operator)
    def notify_to_operator(self):
        self.operator.notify_input_plug_change(self)
    def connect(self, output_plug):
        self.source_plug = output_plug
        # if the source plug changes, propagate the change here
        self.source_plug.on_change.subscribe(self.notify_source_change)
        self.on_change.notify()
    def disconnect(self):
        if not self.connected():
            return  # nothing to do
        try:
            self.source_plug.on_change.unsubscribe(self.notify_source_change)
        except APIRequestErrorOfflineDaemon:
            # self.source_plug comes from a disconnected daemon => no event unsubscribe needed
            pass
        self.source_plug = None
        self.on_change.notify()
    def notify_source_change(self):
        self.on_change.notify()
    def connected(self):
        return self.source_plug is not None
    @property
    def source(self):
        if not self.connected():
            return None
        return self.source_plug.get_source()
    @property
    def enabled(self):
        return self.source is not None
    @property
    def disabled_message(self):
        if self.enabled:
            raise AttributeError
        return 'No source: input plug is not connected or link is disabled!'
    @property
    def columns(self):
        return self.source.columns
    def pack(self):
        info = self.pack_status_info()
        if self.enabled:
            info.update(
                **self.source_plug.pack()
            )
        info.update(label = self.label)
        return info
