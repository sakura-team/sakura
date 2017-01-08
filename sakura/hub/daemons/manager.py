import pickle
from sakura.common.wsapi import APIForwarder, get_remote_api

def rpc_client_manager(daemon_id, context, sock_file):
    print('daemon connected.')
    remote_api = get_remote_api(sock_file, pickle)
    daemon_info = remote_api.get_daemon_info_serializable()
    api_forwarder = APIForwarder(remote_api)
    api_forwarder_ap = api_forwarder.get_access_point()
    context.register_daemon(daemon_id, daemon_info, api_forwarder_ap)
    api_forwarder.run()
    print('daemon disconnected.')

