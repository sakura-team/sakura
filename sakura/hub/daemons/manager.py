import pickle
import gevent.pool
from sakura.hub.db import db_session_wrapper
from sakura.common.io import RemoteAPIForwarder, \
         LocalAPIHandler, api_request_result_interpreter
from sakura.hub.daemons.api import DaemonToHubAPI
from sakura.hub.tools import DaemonDataException
from sakura.common.errors import APIRequestError

def dump_to_sock_file(sock_file, **kwargs):
    pickle.dump(kwargs, sock_file)
    sock_file.flush()

def rpc_client_manager(daemon_info, context, sock_file):
    print('new rpc connection hub (client) -> %s (server).' % daemon_info['name'])
    remote_api = RemoteAPIForwarder(sock_file, pickle, api_request_result_interpreter)
    try:
        with db_session_wrapper():
            daemon_id = context.on_daemon_connect(daemon_info, remote_api)
    except DaemonDataException as e:
        remote_api.fire_data_issue(str(e))
    remote_api.loop()
    with db_session_wrapper():
        context.on_daemon_disconnect(daemon_id)
    print('rpc connection hub (client) -> %s (server) disconnected.' % daemon_info['name'])

def rpc_server_manager(daemon_info, context, sock_file):
    daemon_name = daemon_info['name']
    with db_session_wrapper():
        daemon_id = context.daemons.get(name = daemon_name).id
    print('new rpc connection hub (server) <- %s (client).' % daemon_name)
    pool = gevent.pool.Group()
    local_api = DaemonToHubAPI(daemon_id, context)
    handler = LocalAPIHandler(sock_file, pickle, local_api, pool,
                                session_wrapper = db_session_wrapper)
    handler.loop()
    print('rpc connection hub (server) <- %s (client) disconnected.' % daemon_name)

