import bottle
from gevent.local import local
from sakura.common.bottle import PicklableFileRequest
from sakura.common.errors import APIRequestErrorOfflineDatastore
from sakura.common.tools import ObservableEvent
from sakura.common.events import EventSourceMixin
from sakura.hub.secrets import TemporarySecretsRegistry
from sakura.hub.web.transfers import Transfer
from sakura.common.errors import APIRequestError

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
    def other_login(self, type, ticket, service):
        if type == 'cas':
            import json
            try:
                f = open('hub-authentification.conf', 'r')
            except Exception as e:
                raise APIRequestError('Hub error: Cannot find file <b>hub-authentification.conf</b> !')
                return None

            auths = json.loads(f.read())

            import requests
            format = 'JSON'
            url = auths['cas']['url']
            x = requests.get( url+'?ticket='+ticket+'&format='+format+'&service='+service)
            succ = x.text.find('authenticationSuccess')
            if succ != -1:
                print('CAS AUTHENTICATION SUCCESS')
                login = x.text.split('<cas:user>')[1].split('</cas:user>')[0]
                print('\t Login:', login)
                print()
                found = None
                all_u = tuple(u.pack() for u in self.users.select())
                for u in all_u:
                    if u['login'] == login:
                        found = u
                if found != None:
                    self.session.user = self.users.from_login_or_email(login)
                    return self.session.user.login
                else:
                    print('\tNew user, asking to LDAP for informations ...')
                    #We ask to LDAP
                    import ldap3, ssl

                    try:
                        url = auths['ldap']['url']
                        port = auths['ldap']['port']
                        dn = auths['ldap']['dn']
                        bdn = auths['ldap']['binddn']
                        pw = auths['ldap']['password']
                        if auths['ldap']['tls version'] == 'v1':
                            tls = ldap3.Tls(version = ssl.PROTOCOL_TLSv1)
                    except Exception as e:
                        raise APIRequestError('LDAP description error in <b>hub-authentification.conf</b> !')
                        return None

                    server = ldap3.Server(url+':'+port, tls=tls, get_info=ldap3.ALL, connect_timeout=3.0)

                    try:
                        conn = ldap3.Connection(server, user=bdn, password=pw)
                    except Exception as e:
                        raise APIRequestError('LDAP Connection Failed !')
                        return None

                    try:
                        conn.bind()
                    except Exception as e:
                        raise APIRequestError('LDAP Connection Timeout !<br><b>'+login+'</b> cannot login !')
                        return None

                    entry = conn.search(dn, '(&(objectclass=person)(uid='+l+'))', attributes=['*'])
                    if not entry:
                        raise APIRequestError('<b>'+login+'</b> not found in LDAP server !')
                        return None
                    u = conn.entries[0]

                    # print(u['mail'])
                    # print(u['given name'])
                    # print(u['sn'])

                    user_info = {   'login': login,
                                    'password': '__CAS__',
                                    'email': u['mail'],
                                    'first_name': u['given name'],
                                    'last_name': u['sn'] }

                    if self.users.new_user(**user_info):
                        self.session.user = self.users.from_login_or_email(login)
                        return self.session.user.login
                    return None
            else:
                print('CAS AUTHENTICATION FAILURE', x.text)
                return 'cas authentication failure'
        else:
            return 'Unkown connection type'
