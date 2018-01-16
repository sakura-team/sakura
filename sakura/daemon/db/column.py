import numpy as np

class DBColumn:
    def __init__(self,  table_name,
                        col_name,
                        np_type,
                        select_clause_wrapper,
                        value_wrapper,
                        tags,
                        primary_key,
                        foreign_key_info):
        self.table_name = table_name
        self.col_name = col_name
        self.np_dtype = np.dtype(np_type)
        self.select_clause_wrapper = select_clause_wrapper
        self.value_wrapper = value_wrapper
        self.tags = list(tags)
        self.primary_key = primary_key
        self.foreign_key_info = foreign_key_info
    def pack(self):
        return (self.col_name, str(self.np_dtype), self.tags,
                        self.primary_key, self.foreign_key_info)
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
