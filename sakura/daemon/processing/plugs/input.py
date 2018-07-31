class InputPlug:
    def __init__(self, label):
        self.source_plug = None
        self.label = label
        self.on_change = lambda: None
    def connect(self, output_plug):
        self.source_plug = output_plug
        self.on_change()
    def disconnect(self):
        self.source_plug = None
        self.on_change()
    def connected(self):
        return self.source_plug != None
    @property
    def source(self):
        if not self.connected():
            raise Exception("No source: input plug is not connected!")
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
