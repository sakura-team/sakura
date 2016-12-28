from sakura.daemon.processing.tools import Registry

class Column(object):
    def __init__(self, col_label, col_type, col_index):
        self.label = col_label
        self.type = col_type
        self.index = col_index

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
    def __iter__(self):
        if self.connected():
            return self.source_table.__iter__()
        else:
            return None

CHUNK_SIZE = 1000

class OutputTable(Registry):
    def __init__(self, operator, label, compute_cb):
        self.columns = []
        self.operator = operator
        self.label = label
        self.compute_cb = compute_cb
        self.length = None
    def add_column(self, col_label, col_type):
        return self.register(self.columns, Column, col_label, col_type, len(self.columns))
    def __iter__(self):
        for row in self.compute_cb():
            yield row
