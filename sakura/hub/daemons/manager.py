import pickle
from sakura.common.wsapi import LocalAPIHandler
from sakura.hub.daemons.api import DaemonToHubAPI

def daemon_manager(daemon_id, context, sock_file):
    print('daemon connected.')
    local_api = DaemonToHubAPI(daemon_id, context)
    handler = LocalAPIHandler(sock_file, pickle, local_api)
    handler.loop()
    print('daemon disconnected.')

