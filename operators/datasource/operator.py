#!/usr/bin/env python
import itertools, numpy as np, operator
from sakura.common.cache import cache_result
from sakura.daemon.processing.operator import Operator
from sakura.daemon.processing.parameter import ComboParameter, ParameterException
from sakura.daemon.processing.stream import SQLTableStream
from time import time

class DatabaseSelectionParameter(ComboParameter):
    def __init__(self, label, api):
        super().__init__(label)
        self.api = api
    @cache_result(2)    # this should be mostly constant
    def get_databases(self):
        return sorted(
                self.api.list_readable_databases(),
                key = lambda db: (db['name'], db['database_id']))
    def get_possible_values(self):
        return tuple(db['name'] for db in self.get_databases())
    @property
    def selected_database_id(self):
        if self.value is None:
            return None
        dbs = self.get_databases()
        if len(dbs) > 0 and self.value < len(dbs):
            return dbs[self.value]['database_id']

class TableSelectionParameter(ComboParameter):
    def __init__(self, label, api, db_param):
        super().__init__(label)
        self.api = api
        self.db_param = db_param
    @cache_result(2)    # this should be mostly constant
    def get_tables_of_db(self, database_id):
        return sorted(
                self.api.list_readable_tables(database_id),
                key = lambda t: (t['name'], t['table_id']))
    def get_tables(self):
        database_id = self.db_param.selected_database_id
        if database_id is None:
            return ()
        return self.get_tables_of_db(database_id)
    def get_possible_values(self):
        return tuple(tbl['name'] for tbl in self.get_tables())
    @property
    def selected_table_id(self):
        if self.value is None:
            return None
        return self.get_tables()[self.value]['table_id']

class DataSourceOperator(Operator):
    NAME = "DataSource"
    SHORT_DESC = "Sakura data source stream generator."
    TAGS = [ "source" ]

    def construct(self):
        # parameters
        self.database_param = self.register_parameter(
                DatabaseSelectionParameter('Database', self.api))
        self.table_param = self.register_parameter(
                TableSelectionParameter('Table', self.api, self.database_param))
        self.table_id = None
    @property
    def output_streams(self):
        try:
            if self.database_param.selected_database_id is None:
                self.database_param.auto_fill()
            if self.table_param.selected_table_id is None:
                self.table_param.auto_fill()
        except ParameterException:
            return []   # sorry no table accessible to current user
        table_id = self.table_param.selected_table_id
        if table_id != self.table_id:   # if selection has changed
            self.table_id = table_id
            # store stream object locally to prevent garbage collection
            self.out_stream = self.api.get_table_stream(table_id)
        return [ self.out_stream ]
