import numpy as np, operator, uuid
from sakura.common.ops import LOWER, LOWER_OR_EQUAL, GREATER, GREATER_OR_EQUAL, IN, EQUALS, NOT_EQUALS
from sakura.common.types import sakura_type_to_np_dtype, np_dtype_to_sakura_type, verify_sakura_type_conversion
from sakura.daemon.processing.geo import GeoBoundingBox
from sakura.daemon.processing.condition import SingleColumnFilter, JoinCondition

class ColumnData:
    pass

class ColumnObject:
    pass

class ColumnBase(ColumnObject):
    def __init__(self, col_label, col_type, col_tags, **col_type_params):
        self._label = col_label
        self._tags = col_tags
        self.analyse_type(col_type, **col_type_params)
        self.col_uuid = uuid.uuid4().hex
        self.subcolumns = ()
        self.data = ColumnData()
    def register_subcolumn(self, subcol):
        self.subcolumns += (subcol,)
    def get_uuid(self):
        return self.col_uuid
    def __hash__(self):
        return self.get_uuid()
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

class Column(ColumnBase):
    def __lt__(self, val):
        return SingleColumnFilter(self, LOWER, val)
    def __le__(self, val):
        return SingleColumnFilter(self, LOWER_OR_EQUAL, val)
    def __gt__(self, val):
        return SingleColumnFilter(self, GREATER, val)
    def __ge__(self, val):
        return SingleColumnFilter(self, GREATER_OR_EQUAL, val)
    def __eq__(self, val):
        if isinstance(val, ColumnObject):
            return JoinCondition(self, EQUALS, val)
        else:
            return SingleColumnFilter(self, EQUALS, val)
    def __ne__(self, val):
        return SingleColumnFilter(self, NOT_EQUALS, val)

class GeoSubColumn(ColumnBase):
    def __init__(self, parent_col, component_name, col_type, col_tags, **col_type_params):
        self.parent_col = parent_col
        self.component = 'longitude' if component_name == 'X' else 'latitude'
        col_label = parent_col._label + '.' + component_name
        ColumnBase.__init__(self, col_label, col_type, col_tags, **col_type_params)
    def __lt__(self, val):
        return SingleColumnFilter(self.parent_col, IN, self._get_bbox('lt', val))
    def __le__(self, val):
        return SingleColumnFilter(self.parent_col, IN, self._get_bbox('le', val))
    def __gt__(self, val):
        return SingleColumnFilter(self.parent_col, IN, self._get_bbox('gt', val))
    def __ge__(self, val):
        return SingleColumnFilter(self.parent_col, IN, self._get_bbox('ge', val))
    def _get_bbox(self, op_str, val):
        prefix = 'max_' if op_str in ('lt', 'le') else 'min_'
        bbox_kwargs = { (prefix + self.component): val }
        return GeoBoundingBox(**bbox_kwargs)

class GeoColumn(ColumnBase):
    def __init__(self, *args, **kwargs):
        Column.__init__(self, *args, **kwargs)
        self.X = GeoSubColumn(self, 'X', 'float64', ('longitude',))
        self.register_subcolumn(self.X)
        self.Y = GeoSubColumn(self, 'Y', 'float64', ('latitude',))
        self.register_subcolumn(self.Y)

class BoundColumn(ColumnObject):
    def __init__(self, col, source):
        # col may be a Column or a BoundColumn (if it was bound to another source)
        if isinstance(col, BoundColumn):
            self.column = col.column
            self.added_tags = col.added_tags
        else:
            self.column = col
            self.added_tags = ()
        self.source = source
    def chunks(self, *args, **kwargs):
        for chunk in self.filtered_stream().chunks(*args, **kwargs):
            yield chunk.columns[0]
    def filtered_stream(self):
        return self.source.select(self)
    def add_tags(self, *tags):
        self.added_tags += tags
    def pack(self):
        return self.get_info()
    def get_info(self):
        return self.column._label, self.column._type, (self.column._tags + self.added_tags)
    def __iter__(self):
        for record in self.filtered_stream():
            yield record[0]
    def __getattr__(self, attr):
        return getattr(self.column, attr)
    def __lt__(self, val):
        return self.column < val
    def __le__(self, val):
        return self.column <= val
    def __gt__(self, val):
        return self.column > val
    def __ge__(self, val):
        return self.column >= val
    def __eq__(self, val):
        return self.column == val
    def __ne__(self, val):
        return self.column != val
    def __str__(self):
        return "%s (%s)" % (self.column._label, self.column._type)
