import numpy as np
from sakura.common.types import sakura_type_to_np_dtype

class DBColumn:
    def __init__(self,  table_name,
                        col_name,
                        col_type,
                        select_clause_wrapper,
                        value_wrapper,
                        tags,
                        **params):
        self.table_name = table_name
        self.col_name = col_name
        self.col_type = col_type
        self.np_dtype = sakura_type_to_np_dtype(col_type, **params)
        self.select_clause_wrapper = select_clause_wrapper
        self.value_wrapper = value_wrapper
        self.tags = list(tags)
    def pack(self):
        return (self.col_name, self.col_type, self.tags)
    def to_sql_where_clause(self):
        return '"%(table_name)s"."%(col_name)s"' % dict(
            table_name = self.table_name,
            col_name = self.col_name
        )
    def to_sql_select_clause(self):
        return self.select_clause_wrapper % dict(
            table_name = self.table_name,
            col_name = self.col_name
        )
