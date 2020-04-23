import numpy as np

class DBColumn:
    def __init__(self,  table,
                        col_name,
                        col_type,
                        select_clause_sql,
                        where_clause_sql,
                        sort_clause_sql,
                        value_wrapper,
                        tags,
                        **col_type_params):
        self.table = table
        self.col_name = col_name
        self.col_type = col_type
        self.col_type_params = col_type_params
        self.select_clause_sql = select_clause_sql
        self.where_clause_sql = where_clause_sql
        self.sort_clause_sql = sort_clause_sql
        self.value_wrapper = value_wrapper
        self.subcolumns = ()
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
    def to_sql_sort_clause(self):
        return self.sort_clause_sql
    def add_subcolumn(self, *col_info, **params):
        col = DBColumn(self.table, *col_info, **params)
        self.subcolumns += (col,)
