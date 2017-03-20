import pickle
import gevent.pool
from sakura.common.io import RemoteAPIForwarder, \
                                LocalAPIHandler
from sakura.hub.daemons.api import DaemonToHubAPI

def rpc_client_manager(daemon_info, context, sock_file):
    print('new rpc connection hub (client) -> %s (server).' % daemon_info['name'])
    remote_api = RemoteAPIForwarder(sock_file, pickle)
    daemon_id = context.on_daemon_connect(daemon_info, remote_api)
    remote_api.loop()
    print('rpc connection hub (client) -> %s (server) disconnected.' % daemon_info['name'])
    context.on_daemon_disconnect(daemon_id)

def rpc_server_manager(daemon_info, context, sock_file):
    print('new rpc connection hub (server) <- %s (client).' % daemon_info['name'])
    pool = gevent.pool.Group()
    daemon_id = context.get_daemon_id(daemon_info)
    local_api = DaemonToHubAPI(daemon_id, context)
    handler = LocalAPIHandler(sock_file, pickle, local_api, pool)
    handler.loop()
    print('rpc connection hub (server) <- %s (client) disconnected.' % daemon_info['name'])

