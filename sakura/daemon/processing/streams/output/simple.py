from sakura.daemon.processing.tools import Registry
from sakura.daemon.processing.column import Column

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

