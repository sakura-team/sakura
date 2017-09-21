import numpy as np, operator

class Column(object):
    def __init__(self, col_label, col_type, col_tags,
                output_stream, col_index):
        self.label = col_label
        self.type = col_type
        self.tags = col_tags
        self.output_stream = output_stream
        self.index = col_index
    def pack(self):
        return (self.label, str(np.dtype(self.type)), self.tags)
    def get_dtype(self):
        if self.type == str:
            # string of unknown length: store as object
            # (returning str here would reserve space for 1-char-wide strings only!)
            return self.label, np.object
        else:
            return self.label, self.type
    def __iter__(self):
        for record in self.filtered_stream():
            yield record[0]
    def chunks(self, *args, **kwargs):
        for chunk in self.filtered_stream().chunks(*args, **kwargs):
            yield chunk.columns[0]
    def filtered_stream(self):
        return self.output_stream.select_columns(self)
    def add_tags(self, *tags):
        self.tags += tags
    def __lt__(self, other):
        return (self, operator.__lt__, other)
    def __le__(self, other):
        return (self, operator.__le__, other)
    def __eq__(self, other):
        return (self, operator.__eq__, other)
    def __ne__(self, other):
        return (self, operator.__ne__, other)
    def __gt__(self, other):
        return (self, operator.__gt__, other)
    def __ge__(self, other):
        return (self, operator.__ge__, other)
