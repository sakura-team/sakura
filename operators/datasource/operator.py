#!/usr/bin/env python
import itertools, numpy as np, operator
from sakura.daemon.processing.operator import Operator
from sakura.daemon.processing.parameter import ComboParameter
from sakura.daemon.processing.stream import SQLTableStream
from time import time

class DatabaseSelectionParameter(ComboParameter):
    def __init__(self, label, op):
        super().__init__(label)
        self.op = op
    def iter_databases(self):
        for ds_key in sorted(self.op.daemon.datastores.keys()):
            ds = self.op.daemon.datastores[ds_key]
            if ds.online:
                for db_key in sorted(ds.databases.keys()):
                    yield ds.databases[db_key]
    def get_possible_values(self):
        return tuple(db.db_name for db in self.iter_databases())
    @property
    def selected_database(self):
        if self.value is None:
            return None
        dbs = tuple(self.iter_databases())
        if len(dbs) > 0 and self.value < len(dbs):
            return dbs[self.value]

class TableSelectionParameter(ComboParameter):
    def __init__(self, label, op):
        super().__init__(label)
        self.op = op
    @property
    def tables(self):
        database = self.op.database_param.selected_database
        if database is None:
            return ()
        return tuple(database.tables[k]
             for k in sorted(database.tables.keys()))
    def get_possible_values(self):
        return tuple(tbl.name for tbl in self.tables)
    @property
    def selected_table(self):
        if self.value is None:
            return None
        return self.tables[self.value]

class DataSourceOperator(Operator):
    NAME = "DataSource"
    SHORT_DESC = "Sakura data source stream generator."
    TAGS = [ "source" ]

    def construct(self):
        # parameters
        self.database_param = self.register_parameter(
                DatabaseSelectionParameter('Database', self))
        self.table_param = self.register_parameter(
                TableSelectionParameter('Table', self))
    @property
    def output_streams(self):
        if self.database_param.selected_database is None:
            self.database_param.auto_fill()
        if self.table_param.selected_table is None:
            self.table_param.auto_fill()
        table = self.table_param.selected_table
        return [ table.stream ]
