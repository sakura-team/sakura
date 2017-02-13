from sakura.daemon.processing.tools import Registry

class Column(object):
    def __init__(self, col_label, col_type, output_table, col_index):
        self.label = col_label
        self.type = col_type
        self.output_table = output_table
        self.index = col_index
    def get_info_serializable(self):
        return (self.label, self.type.__name__)
    def __iter__(self):
        for row in self.output_table:
            yield row[self.index]

class InputTable(object):
    def __init__(self, label):
        self.source_table = None
        self.columns = None
        self.label = label
    def connect(self, output_table):
        self.source_table = output_table
        self.columns = self.source_table.columns
    def disconnect(self):
        self.source_table = None
        self.columns = None
    def connected(self):
        return self.source_table != None
    def columns(self):
        return self.columns
    def get_info_serializable(self):
        info = dict(label = self.label)
        if self.connected():
            info.update(
                connected = True,
                columns = [ col.get_info_serializable() for col in self.columns ],
                length = self.source_table.length
            )
        else:
            info.update(
                connected = False
            )
        return info
    def __iter__(self):
        if self.connected():
            return self.source_table.__iter__()
        else:
            return None
    def get_range(self, *args):
        if self.connected():
            return self.source_table.get_range(*args)
        else:
            return None

class OutputTable(Registry):
    def __init__(self, operator, label, compute_cb):
        self.columns = []
        self.operator = operator
        self.label = label
        self.compute_cb = compute_cb
        self.length = None
    def add_column(self, col_label, col_type):
        return self.register(self.columns, Column, col_label, col_type, self, len(self.columns))
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

# internal streams and output tables are the same
# object.
class InternalStream(OutputTable):
    pass

