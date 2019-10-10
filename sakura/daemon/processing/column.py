import numpy as np, operator
from sakura.common.types import sakura_type_to_np_dtype, np_dtype_to_sakura_type, verify_sakura_type_conversion


class Column(object):
    def __init__(self, col_label, col_type, col_tags,
                 output_stream, col_index, **col_type_params):
        self._label = col_label
        self._tags = col_tags
        self.output_stream = output_stream
        self._index = col_index
        self.analyse_type(col_type, **col_type_params)

    def analyse_type(self, col_type, **col_type_params):
        if isinstance(col_type, (type, tuple)):
            # type written as numpy dtype arguments
            self._type, self._type_params = np_dtype_to_sakura_type(np.dtype(col_type))
            self._type_params.update(**col_type_params)
        else:
            # type written as a sakura type
            self._type = col_type
            self._type_params = col_type_params

    def pack(self):
        return self._label, self._type, self._tags

    def get_dtype(self):
        return self._label, sakura_type_to_np_dtype(self._type, **self._type_params)

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

    def set_type(self, in_type):
        verify_sakura_type_conversion(self._type, in_type)
        self._type = in_type
