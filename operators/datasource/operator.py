#!/usr/bin/env python
import itertools, numpy as np, operator
from sakura.daemon.processing.operator import Operator
from sakura.daemon.processing.parameter import ComboParameter, ParameterException
from sakura.daemon.processing.source import SQLTableSource
from time import time

class DatabaseSelectionParameter(ComboParameter):
    def __init__(self, label, api):
        super().__init__(label)
        self.api = api
    def get_possible_items(self):
        # combo label is database name
        # combo identifier value is database_id
        # combo ordering is based on (label, database_id)
        return sorted([(db['database_id'], db['name']) for db in \
                                self.api.list_readable_databases()],
                      key = lambda db_tuple: db_tuple[::-1])
    @property
    def selected_database_id(self):
        return self.value

class TableSelectionParameter(ComboParameter):
    def __init__(self, label, api, db_param):
        super().__init__(label)
        self.api = api
        self.db_param = db_param
    def get_possible_items(self):
        database_id = self.db_param.selected_database_id
        if database_id is None:
            return ()
        # combo label is table name
        # combo identifier value is table_id
        # combo ordering is based on (label, table_id)
        return sorted([(tbl['table_id'], tbl['name']) for tbl in \
                                self.api.list_readable_tables(database_id)],
                      key = lambda tbl_tuple: tbl_tuple[::-1])
    @property
    def selected_table_id(self):
        return self.value

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
        self.output_plug = self.register_output('Database table data')
        self.api.subscribe_global_event('on_datastores_change', self.on_ds_change)
        self.database_param.on_change.subscribe(self.on_db_change)
        self.table_param.on_change.subscribe(self.on_tbl_change)

    def on_ds_change(self):
        print('ds: on_ds_change')
        self.database_param.recheck()

    def on_db_change(self):
        print('ds: on_db_change')
        self.table_param.recheck()

    def on_tbl_change(self):
        print('ds: on_tbl_change')
        table_id = self.table_param.selected_table_id
        if table_id is None:
            self.output_plug.source = None
        else:
            self.output_plug.source = self.api.get_table_source(table_id)
