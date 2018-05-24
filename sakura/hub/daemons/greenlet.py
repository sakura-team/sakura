
import pickle
from gevent.server import StreamServer
from sakura.hub.daemons.manager import \
            rpc_client_manager, rpc_server_manager
from sakura.common.tools import monitored
import sakura.hub.conf as conf
from enum import Enum

GreenletModes = Enum('GreenletModes', 'RPC_CLIENT RPC_SERVER')

def daemons_greenlet(context):
    @monitored
    def handle(socket, address):
        sock_file = socket.makefile(mode='rwb')
        while True:
            req, daemon_name = pickle.load(sock_file)
            if req == b'RPC_SERVER':
                # if the remote end says 'server', we are client :)
                rpc_client_manager(context, daemon_name, sock_file)
                break
            elif req == b'RPC_CLIENT':
                # if the remote end says 'client', we are server :)
                rpc_server_manager(context, daemon_name, sock_file)
                break
    server = StreamServer(('0.0.0.0', conf.hub_port), handle)
    server.start()
    # wait for end or exception
    handle.catch_issues()

