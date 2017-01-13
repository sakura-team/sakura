import pickle
from sakura.common.wsapi import APIForwarder, get_remote_api, \
                                LocalAPIHandler
from sakura.hub.daemons.api import DaemonToHubAPI

def rpc_client_manager(daemon_id, context, sock_file):
    print('new rpc connection hub (client) -> daemon %d (server).' % daemon_id)
    remote_api = get_remote_api(sock_file, pickle)
    daemon_info = remote_api.get_daemon_info_serializable()
    api_forwarder = APIForwarder(remote_api)
    api_forwarder_ap = api_forwarder.get_access_point()
    context.register_daemon(daemon_id, daemon_info, api_forwarder_ap)
    api_forwarder.run()
    print('rpc connection hub (client) -> daemon %d (server) disconnected.' % daemon_id)

def rpc_server_manager(daemon_id, context, sock_file):
    print('new rpc connection hub (server) <- daemon %d (client).' % daemon_id)
    local_api = DaemonToHubAPI(daemon_id, context)
    handler = LocalAPIHandler(sock_file, pickle, local_api)
    handler.loop()
    print('rpc connection hub (server) <- daemon %d (client) disconnected.' % daemon_id)

