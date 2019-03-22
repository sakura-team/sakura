import numpy as np
from sakura.common.types import sakura_type_to_np_dtype

class DBColumn:
    def __init__(self,  table,
                        col_name,
                        col_type,
                        select_clause_sql,
                        where_clause_sql,
                        value_wrapper,
                        tags,
                        **params):
        self.table = table
        self.col_name = col_name
        self.col_type = col_type
        self.np_dtype = sakura_type_to_np_dtype(col_type, **params)
        self.select_clause_sql = select_clause_sql
        self.where_clause_sql = where_clause_sql
        self.value_wrapper = value_wrapper
    @property
    def tags(self):
        for col, col_tags in zip(self.table.columns, self.table.col_tags_info):
            if col is self:
                return col_tags
    def pack(self):
        return (self.col_name, self.col_type)
    def to_sql_where_clause(self):
        return self.where_clause_sql
    def to_sql_select_clause(self):
        return self.select_clause_sql
