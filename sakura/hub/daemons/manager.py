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

def on_daemon_connect(context, daemon_id):
    with db_session_wrapper():
        daemon = context.daemons[daemon_id]
        try:
            daemon.on_connect()
        except DaemonDataError as e:
            daemon.api.fire_data_issue(str(e))

def rpc_client_manager(context, daemon_name, sock_file):
    print('new rpc connection hub (client) -> %s (server).' % daemon_name)
    remote_api = RemoteAPIForwarder(sock_file, pickle)
    with db_session_wrapper():
        daemon = context.get_daemon_from_name(daemon_name)
        daemon.save_api(remote_api)
        # We will have to run daemon.on_connect()
        # but this greenlet cannot handle it because it may involve
        # IO messages on this remote_api we have to manage.
        # So we delegate this to the planner greenlet, and this greenlet
        # can focus on managing this remote_api.
        daemon_id = daemon.id
        context.planner.run_once(
               lambda: on_daemon_connect(context, daemon_id))
    # start remote_api management loop
    remote_api.loop()
    # loop has ended => daemon is disconnected!
    with db_session_wrapper():
        context.daemons[daemon_id].on_disconnect()
    print('rpc connection hub (client) -> %s (server) disconnected.' % daemon_name)

def rpc_server_manager(context, daemon_name, sock_file):
    print('new rpc connection hub (server) <- %s (client).' % daemon_name)
    pool = gevent.pool.Group()
    local_api = DaemonToHubAPI(context)
    handler = LocalAPIHandler(sock_file, PickleLocalAPIProtocol, local_api, pool,
                                session_wrapper = db_session_wrapper)
    handler.loop()
    print('rpc connection hub (server) <- %s (client) disconnected.' % daemon_name)

