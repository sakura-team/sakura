class InputStream(object):
    def __init__(self, label):
        self.source_stream = None
        self.columns = None
        self.label = label
    def connect(self, output_stream):
        self.source_stream = output_stream
        self.columns = self.source_stream.columns
    def disconnect(self):
        self.source_stream = None
        self.columns = None
    def connected(self):
        return self.source_stream != None
    def columns(self):
        return self.columns
    def pack(self):
        info = {}
        if self.connected():
            info.update(
                connected = True,
                **self.source_stream.pack()
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
            return self.source_stream.get_range(*args, **kwargs)
        else:
            return None
    def __getattr__(self, attr):
        # redirect calls to the connected output stream
        if self.connected():
            return getattr(self.source_stream, attr)
        else:
            return None
    def __iter__(self):
        # explicitely redirect this one
        # (such a 'special method' is not matched by the
        # __getattr__() function above)
        if self.connected():
            return self.source_stream.__iter__()
        else:
            return None
