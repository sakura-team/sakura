from sakura.daemon.processing.tools import Registry

class Column(object):
    def __init__(self, col_label, col_type, col_tags,
                output_stream, col_index):
        self.label = col_label
        self.type = col_type
        self.tags = col_tags
        self.output_stream = output_stream
        self.index = col_index
    def get_info_serializable(self):
        return (self.label, self.type.__name__, self.tags)
    def __iter__(self):
        for row in self.output_stream:
            yield row[self.index]

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
    def get_info_serializable(self):
        info = dict(label = self.label)
        if self.connected():
            info.update(
                connected = True,
                columns = [ col.get_info_serializable() for col in self.columns ],
                length = self.source_stream.length
            )
        else:
            info.update(
                connected = False
            )
        return info
    def __iter__(self):
        if self.connected():
            return self.source_stream.__iter__()
        else:
            return None
    def get_range(self, *args):
        if self.connected():
            return self.source_stream.get_range(*args)
        else:
            return None

class SimpleStream(Registry):
    def __init__(self, label, compute_cb):
        self.columns = []
        self.label = label
        self.compute_cb = compute_cb
        self.length = None
    def add_column(self, col_label, col_type, col_tags=()):
        return self.register(self.columns, Column,
                    col_label, col_type, tuple(col_tags),
                    self, len(self.columns))
    def get_info_serializable(self):
        return dict(label = self.label,
                    columns = [ col.get_info_serializable() for col in self.columns ],
                    length = self.length)
    def __iter__(self):
        for row in self.compute_cb():
            yield row
    def get_range(self, row_start, row_end):
        rows = []
        row_idx = 0
        for row in self:
            if row_idx == row_end:
                break
            if row_start <= row_idx:
                rows.append(row)
            row_idx += 1
        return rows

# internal streams and output streams are the same
# object.
class InternalStream(SimpleStream):
    pass

