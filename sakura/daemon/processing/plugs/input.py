from sakura.common.errors import APIRequestError, APIRequestErrorOfflineDaemon
from sakura.common.tools import ObservableEvent

class InputPlug:
    def __init__(self, label):
        self.source_plug = None
        self.label = label
        self.on_change = ObservableEvent()
    def connect(self, output_plug):
        self.source_plug = output_plug
        # if the source plug changes, propagate the change here
        self.source_plug.on_change.subscribe(self.notify_source_change)
        self.on_change.notify()
    def disconnect(self):
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
        return self.source_plug != None
    @property
    def source(self):
        if not self.connected():
            raise APIRequestError("No source: input plug is not connected or link is disabled!")
        return self.source_plug.source
    @property
    def columns(self):
        return self.source.columns
    def pack(self):
        info = {}
        if self.connected():
            info.update(
                connected = True,
                **self.source_plug.pack()
            )
        else:
            info.update(
                connected = False
            )
        info.update(label = self.label)
        return info
    def get_range(self, *args, **kwargs):
        # redirect call to the connected output stream
        if self.connected():
            return self.source_plug.get_range(*args, **kwargs)
        else:
            return None
    def get_columns_info(self):
        if self.connected():
            return self.source_plug.get_columns_info()
        else:
            return None
    def __iter__(self):
        if self.connected():
            return self.source_plug.__iter__()
        else:
            return None
