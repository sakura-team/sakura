class InputPlug:
    def __init__(self, label):
        self.source_plug = None
        self.columns = None
        self.label = label
    def connect(self, output_plug):
        self.source_plug = output_plug
        self.columns = self.source_plug.columns
    def disconnect(self):
        self.source_plug = None
        self.columns = None
    def connected(self):
        return self.source_plug != None
    def columns(self):
        return self.columns
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
    def __getattr__(self, attr):
        # redirect calls to the connected output stream
        if self.connected():
            return getattr(self.source_plug, attr)
        else:
            return None
    def __iter__(self):
        # explicitely redirect this one
        # (such a 'special method' is not matched by the
        # __getattr__() function above)
        if self.connected():
            return self.source_plug.__iter__()
        else:
            return None
