import numpy as np
from sakura.common.types import sakura_type_to_np_dtype

class DBColumn:
    def __init__(self,  table,
                        col_name,
                        col_type,
                        select_clause_wrapper,
                        value_wrapper,
                        tags,
                        **params):
        self.table = table
        self.col_name = col_name
        self.col_type = col_type
        self.np_dtype = sakura_type_to_np_dtype(col_type, **params)
        self.select_clause_wrapper = select_clause_wrapper
        self.value_wrapper = value_wrapper
    @property
    def tags(self):
        daemon_name = self.table.db.dbms.engine.name
        ds_host = self.table.db.dbms.host
        ds_driver_label = self.table.db.dbms.driver_label
        db_name = self.table.db.db_name
        table_name = self.table.name
        col_name = self.col_name
        hub_api = self.table.db.dbms.engine.hub
        return hub_api.get_col_tags(daemon_name, ds_host, ds_driver_label,
                                    db_name, table_name, col_name)
    def pack(self):
        return (self.col_name, self.col_type)
    def to_sql_where_clause(self):
        return '"%(table_name)s"."%(col_name)s"' % dict(
            table_name = self.table.name,
            col_name = self.col_name
        )
    def to_sql_select_clause(self):
        return self.select_clause_wrapper % dict(
            table_name = self.table.name,
            col_name = self.col_name
        )
