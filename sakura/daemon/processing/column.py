import numpy as np, operator


class Column(object):
    def __init__(self, col_label, col_type, col_tags,
                 output_stream, col_index):
        self._label = col_label
        self._type = col_type
        self._tags = col_tags
        self.output_stream = output_stream
        self._index = col_index

    def pack(self):
        return self._label, str(np.dtype(self._type)), self._tags

    def get_dtype(self):
        if self._type == str:
            # string of unknown length: store as object
            # (returning str here would reserve space for 1-char-wide strings only!)
            return self._label, np.object
        else:
            return self._label, self._type

    def __iter__(self):
        for record in self.filtered_stream():
            yield record[0]

    def chunks(self, *args, **kwargs):
        for chunk in self.filtered_stream().chunks(*args, **kwargs):
            yield chunk.columns[0]

    def filtered_stream(self):
        return self.output_stream.select_columns(self._index)

    def add_tags(self, *tags):
        self._tags += tags
