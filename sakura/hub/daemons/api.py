from contextlib import contextmanager
from sakura.hub.db import db_session_wrapper
from sakura.hub.context import greenlet_env
from sakura.common.io import pack
from sakura.common.access import GRANT_LEVELS

def get_operator_session_wrapper(op_id):
    @contextmanager
    def operator_session_wrapper():
        # record op_id
        greenlet_env.op_id = op_id
        # call db session wrapper
        with db_session_wrapper():
            yield
    return operator_session_wrapper

class OperatorToHubAPI:
    def __init__(self, context):
        self.context = context
    @property
    def databases(self):
        return self.context.databases.filter_for_current_user()
    @property
    def tables(self):
        return self.context.tables.filter_for_current_user()
    def list_readable_databases(self):
        result = []
        for db in self.databases:
            if db.readable:
                db.update_tables_from_daemon()
                if len(db.tables) > 0:
                    result.append(db.pack())
        return result
    def list_readable_tables(self, database_id):
        db = self.databases[database_id]
        if not db.readable:
            return ()
        return pack(db.tables)
    def get_table_source(self, table_id):
        table = self.tables[table_id]
        if not table.readable:
            return None
        return table.remote_instance.stream

class WrappedOperatorToHubAPI:
    def __init__(self, op_api, op_id):
        self.op_api = op_api
        self.op_session_wrapper = get_operator_session_wrapper(op_id)
    def __getattr__(self, attr):
        with self.op_session_wrapper():
            return getattr(self.op_api, attr)

class OperatorAPIs:
    def __init__(self, context):
        self.operator_api = OperatorToHubAPI(context)
    def __getitem__(self, op_id):
        return WrappedOperatorToHubAPI(self.operator_api, op_id)

class DaemonToHubAPI(object):
    def __init__(self, context):
        self.context = context
        self.operator_apis = OperatorAPIs(context)
    def get_login_from_email(self, email):
        u = self.context.users.get(email=email)
        if u is None:
            return None
        return u.login
    def get_col_tags(self, daemon_name, ds_host, ds_driver_label,
                        db_name, table_name, col_name):
        daemon = self.context.daemons.get(name = daemon_name)
        datastore = self.context.datastores.get(daemon = daemon,
                            host = ds_host, driver_label = ds_driver_label)
        database = self.context.databases.get(datastore = datastore,
                            name = db_name)
        table = self.context.tables.get(database = database,
                            name = table_name)
        column = self.context.columns.get(table = table,
                            col_name = col_name)
        return column.user_tags
