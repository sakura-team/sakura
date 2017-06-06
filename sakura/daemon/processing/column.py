import numpy as np

class Column(object):
    def __init__(self, col_label, col_type, col_tags,
                output_stream, col_index):
        self.label = col_label
        self.type = col_type
        self.tags = col_tags
        self.output_stream = output_stream
        self.index = col_index
    def get_info_serializable(self):
        return (self.label, str(np.dtype(self.type)), self.tags)
    def __iter__(self):
        for record in self.filtered_stream():
            yield record[0]
    def chunks(self, *args, **kwargs):
        for chunk in self.filtered_stream().chunks():
            yield chunk.columns[0]
    def filtered_stream(self):
        return self.output_stream.select_columns(self)
    def add_tags(self, *tags):
        self.tags += tags
