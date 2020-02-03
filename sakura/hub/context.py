import bottle
from gevent.local import local
from sakura.common.bottle import PicklableFileRequest
from sakura.common.errors import APIRequestErrorOfflineDatastore
from sakura.common.tools import ObservableEvent
from sakura.common.events import EventSourceMixin
from sakura.hub.secrets import TemporarySecretsRegistry
from sakura.hub.web.transfers import Transfer

# object storing greenlet-local data
greenlet_env = local()

def get_context():
    return HubContext._instance

# handle keyword 'current' keyword as a user login name
class UsersWrapper:
    def __init__(self, users):
        self.users = users
    def __getitem__(self, login):
        if login == 'current':
            return get_context().user
        else:
            return self.users[login]
    def __getattr__(self, attr):
        return getattr(self.users, attr)

class HubContext(EventSourceMixin):
    _instance = None
    PW_RECOVERY_SECRETS_LIFETIME = 10 * 60
    class global_events:
        on_datastores_change = ObservableEvent()
    def __init__(self, db, planner):
        self.db = db
        self.planner = planner
        self.daemons = self.db.Daemon
        self.dataflows = self.db.Dataflow
        self.projects = self.db.Project
        self.pages = self.db.ProjectPage
        self.users = UsersWrapper(self.db.User)
        self.sessions = self.db.Session
        self.op_classes = self.db.OpClass
        self.op_instances = self.db.OpInstance
        self.links = self.db.Link
        self.op_params = self.db.OpParam
        self.datastores = self.db.Datastore
        self.databases = self.db.Database
        self.tables = self.db.DBTable
        self.columns = self.db.DBColumn
        self.pw_recovery_secrets = TemporarySecretsRegistry(
                        HubContext.PW_RECOVERY_SECRETS_LIFETIME)
        self.transfers = {}
        HubContext._instance = self
    def restore(self):
        self.op_classes.restore()
    @property
    def session(self):
        session_id = getattr(greenlet_env, 'session_id', None)
        if session_id is None:
            #print("SESSION ID IS NONE")
            # we are probably processing a request coming from a daemon
            return None
        session = self.sessions.get(id=session_id)
        if session is None:
            bottle.abort(401, 'Wrong session id.')
        return session
    @property
    def operator(self):
        op_id = getattr(greenlet_env, 'op_id', None)
        if op_id is None:
            # we are processing a request coming from the web API
            return None
        return self.op_instances[op_id]
    @property
    def user(self):
        user = None
        if self.session is not None:
            user = self.session.user
        elif self.operator is not None:
            owner = self.operator.dataflow.owner
            user = self.users[owner]
        if user is None:
            return self.users.anonymous()
        else:
            return user
    def user_is_logged_in(self):
        return not self.user.is_anonymous()
    def attach_session(self, session_id):
        if session_id is not None and \
                self.sessions.get(id = session_id) is not None:
            greenlet_env.session_id = session_id
            self.session.renew()
            return True
        else:
            return False
    def new_session(self):
        # create a new session
        session = self.sessions.new_session(self)
        greenlet_env.session_id = session.id
        print('new session created ' + str(session.id))
    def get_daemon_from_name(self, daemon_name):
        return self.daemons.get_or_create(daemon_name)
    def create_link(self, src_op_id, src_out_id, dst_op_id, dst_in_id):
        src_op = self.op_instances[src_op_id]
        dst_op = self.op_instances[dst_op_id]
        link = self.links.create_link(src_op, src_out_id, dst_op, dst_in_id)
        self.db.commit()    # refresh link id
        return link.id
    def get_possible_links(self, src_op_id, dst_op_id):
        src_op = self.op_instances[src_op_id]
        dst_op = self.op_instances[dst_op_id]
        return self.links.get_possible_links(src_op, dst_op)
    def serve_operator_file(self, op_id, filepath):
        op = self.op_instances.get(id = op_id)
        if op is None:
            return bottle.HTTPError(404, "No such operator instance.")
        request = PicklableFileRequest(bottle.request, filepath)
        resp = op.serve_file(request)
        if resp[0] == True:
            return bottle.HTTPResponse(*resp[1:])
        else:
            return bottle.HTTPError(*resp[1:])
    def start_transfer(self):
        transfer = Transfer(self)
        self.transfers[transfer.transfer_id] = transfer
        return transfer.transfer_id
    def get_transfer_status(self, transfer_id):
        status = self.transfers[transfer_id].get_status()
        if status['status'] == 'done':
            del self.transfers[transfer_id]
        return status
    def abort_transfer(self, transfer_id):
        status = self.transfers[transfer_id].get_status()
        if status['status'] == 'done':
            # transfer is already completed!
            del self.transfers[transfer_id]
        else:
            self.transfers[transfer_id].abort()
    def attach_api_exception_handlers(self, daemon_api):
        daemon_api.on_remote_exception.subscribe(self.on_api_exception)
    def on_api_exception(self, exc):
        if isinstance(exc, APIRequestErrorOfflineDatastore):
            # datastore offline exception, refresh the status we have here at the hub
            ds_host, ds_driver_label = exc.data['host'], exc.data['driver_label']
            datastore = self.datastores.get(host = ds_host, driver_label = ds_driver_label)
            datastore.refresh()
    def login(self, login_or_email, password):
        self.session.user = self.users.from_credentials(login_or_email, password)
        return self.session.user.login
