import pickle
import gevent.pool
from sakura.hub.db import db_session_wrapper
from sakura.common.io import LocalAPIHandler, \
                RemoteAPIForwarder, PickleLocalAPIProtocol
from sakura.hub.daemons.api import DaemonToHubAPI
from sakura.hub.exceptions import DaemonDataError
from sakura.common.errors import APIRequestError

def dump_to_sock_file(sock_file, **kwargs):
    pickle.dump(kwargs, sock_file)
    sock_file.flush()

def rpc_client_manager(context, daemon_name, sock_file):
    print('new rpc connection hub (client) -> %s (server).' % daemon_name)
    remote_api = RemoteAPIForwarder(sock_file, pickle)
    try:
        with db_session_wrapper():
            daemon_id = context.on_daemon_connect(remote_api)
    except DaemonDataError as e:
        remote_api.fire_data_issue(str(e))
    remote_api.loop()
    with db_session_wrapper():
        context.on_daemon_disconnect(daemon_id)
    print('rpc connection hub (client) -> %s (server) disconnected.' % daemon_name)

def rpc_server_manager(context, daemon_name, sock_file):
    print('new rpc connection hub (server) <- %s (client).' % daemon_name)
    pool = gevent.pool.Group()
    local_api = DaemonToHubAPI(context)
    handler = LocalAPIHandler(sock_file, PickleLocalAPIProtocol, local_api, pool,
                                session_wrapper = db_session_wrapper)
    handler.loop()
    print('rpc connection hub (server) <- %s (client) disconnected.' % daemon_name)

