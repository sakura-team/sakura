import gevent
from contextlib import contextmanager
from sakura.hub.db import db_session_wrapper
from sakura.hub.context import greenlet_env
from sakura.common.io import pack
from sakura.common.access import GRANT_LEVELS

# We must associate the op_id with each started greenlet in
# order to apply the access grants of the owner of the dataflow
def get_operator_session_wrapper(op_id):
    @contextmanager
    def operator_session_wrapper():
        # record op_id
        greenlet_env.op_id = op_id
        # call db session wrapper
        with db_session_wrapper():
            yield
    return operator_session_wrapper

def spawn(f, *args):
    op_id = greenlet_env.op_id
    def wrap_f(*args):
        greenlet_env.op_id = op_id
        f(*args)
    return gevent.spawn(wrap_f, *args)

class OperatorToHubAPI:
    def __init__(self, context):
        self.context = context
    @property
    def databases(self):
        self.context.datastores.refresh_offline_datastores()
        return self.context.databases.filter_for_current_user()
    @property
    def tables(self):
        self.context.datastores.refresh_offline_datastores()
        return self.context.tables.filter_for_current_user()
    def list_readable_databases(self):
        result = []
        greenlets = []
        # this can be quite long if communication with the datastore
        # takes time, so do it in parallel
        def append_db_info(db):
            db.update_tables_from_daemon()
            if len(db.tables) > 0:
                result.append(db.pack())
        for db in self.databases:
            if db.readable:
                g = spawn(append_db_info, db)
                greenlets.append(g)
        gevent.joinall(greenlets)
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
        return table.remote_instance.source()
    def subscribe_global_event(self, event_name, cb):
        evt_manager = getattr(self.context.global_events, event_name)
        evt_manager.subscribe(cb)

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
