import numpy as np, operator, uuid
from sakura.common.errors import APIRequestError
from sakura.common.types import sakura_type_to_np_dtype, np_dtype_to_sakura_type, verify_sakura_type_conversion

class AndColumnFilters:
    def __init__(self, *filters):
        self.filters = filters
    def __and__(self, other):
        filters = list(self.filters) + [other]
        return AndColumnFilters(*filters)
    def filtered_source(self, source):
        for f in self.filters:
            source = f.filtered_source(source)
        return source

class SingleColumnFilter:
    def __init__(self, column, op, value):
        self.column = column
        self.op = op
        self.value = value
    def __and__(self, other):
        return AndColumnFilters(self, other)
    def filtered_source(self, source):
        col_index = source._get_col_index(self.column)
        if col_index is None:
            raise APIRequestError('Filter cannot be applied because column does not belong to this source.')
        return source.__filter__(col_index, self.op, self.value)

class Column(object):
    def __init__(self, col_label, col_type, col_tags, **col_type_params):
        self._label = col_label
        self._tags = col_tags
        self.analyse_type(col_type, **col_type_params)
        self.col_uuid = uuid.uuid4().hex

    def get_uuid(self):
        return self.col_uuid

    def __hash__(self):
        return self.get_uuid()

    def __eq__(self, other):
        return self.col_uuid == other.get_uuid()

    def analyse_type(self, col_type, **col_type_params):
        if isinstance(col_type, (type, tuple)):
            # type written as numpy dtype arguments
            self._type, self._type_params = np_dtype_to_sakura_type(np.dtype(col_type))
            self._type_params.update(**col_type_params)
        else:
            # type written as a sakura type
            self._type = col_type
            self._type_params = col_type_params

    def get_dtype(self):
        return self._label, sakura_type_to_np_dtype(self._type, **self._type_params)

    def set_type(self, in_type):
        verify_sakura_type_conversion(self._type, in_type)
        self._type = in_type

    def __lt__(self, val):
        return SingleColumnFilter(self, operator.__lt__, val)

    def __le__(self, val):
        return SingleColumnFilter(self, operator.__le__, val)

    def __gt__(self, val):
        return SingleColumnFilter(self, operator.__gt__, val)

    def __ge__(self, val):
        return SingleColumnFilter(self, operator.__ge__, val)

class BoundColumn:
    def __init__(self, column, source):
        self.column = column
        self.source = source
        self.added_tags = ()

    def chunks(self, *args, **kwargs):
        for chunk in self.filtered_stream().chunks(*args, **kwargs):
            yield chunk.columns[0]

    def filtered_stream(self):
        return self.source.select(self)

    def add_tags(self, *tags):
        self.added_tags += tags

    @property
    def _label(self):
        return self.column._label

    def pack(self):
        return self.get_info()

    def get_info(self):
        return self.column._label, self.column._type, (self.column._tags + self.added_tags)

    def __iter__(self):
        for record in self.filtered_stream():
            yield record[0]

    def __lt__(self, val):
        return self.column < val

    def __le__(self, val):
        return self.column <= val

    def __gt__(self, val):
        return self.column > val

    def __ge__(self, val):
        return self.column >= val

