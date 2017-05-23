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
