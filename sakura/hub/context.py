import bottle
from sakura.common.bottle import PicklableFileRequest
from sakura.hub.db import instanciate_db
from sakura.hub.secrets import SecretsRegistry

class HubContext(object):
    SESSION_SECRETS_LIFETIME = 5
    def __init__(self):
        self.db = instanciate_db()
        self.daemons = self.db.Daemon
        self.projects = self.db.Project
        self.users = self.db.User
        self.sessions = self.db.Session
        self.op_classes = self.db.OpClass
        self.op_instances = self.db.OpInstance
        self.links = self.db.Link
        self.op_params = self.db.OpParam
        self.datastores = self.db.Datastore
        self.databases = self.db.Database
        self.tables = self.db.DBTable
        self.columns = self.db.DBColumn
        self.session_secrets = SecretsRegistry(
                        HubContext.SESSION_SECRETS_LIFETIME)
    def new_session(self):
        return self.sessions.new_session(self)
    def get_session(self, session_secret):
        return self.session_secrets.get_obj(session_secret)
    def on_daemon_connect(self, daemon_info, api):
        daemon = self.daemons.restore_daemon(self, api = api, **daemon_info)
        return daemon.id
    def on_daemon_disconnect(self, daemon_id):
        self.daemons[daemon_id].connected = False
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
