
from gevent.server import StreamServer
from sakura.hub.daemons.manager import \
            rpc_client_manager, rpc_server_manager
from sakura.hub.tools import monitored
import sakura.hub.conf as conf
from enum import Enum

GreenletModes = Enum('GreenletModes', 'RPC_CLIENT RPC_SERVER')

def daemons_greenlet(context):
    @monitored
    def handle(socket, address):
        sock_file = socket.makefile(mode='rwb')
        mode, daemon_id = None, None
        while True:
            req = sock_file.readline().strip()
            if req == b'GETID':
                daemon_id = context.get_daemon_id()
                sock_file.write(("%d\n" % daemon_id).encode("ascii"))
                sock_file.flush()
            elif req == b'SETID':
                daemon_id = int(sock_file.readline().strip())
            elif req == b'RPC_SERVER':
                # if the remote end says 'server', we are client :)
                mode = GreenletModes.RPC_CLIENT
                break
            elif req == b'RPC_CLIENT':
                # if the remote end says 'client', we are server :)
                mode = GreenletModes.RPC_SERVER
                break
        print(mode, daemon_id)
        if mode == GreenletModes.RPC_CLIENT:
            rpc_client_manager(daemon_id, context, sock_file)
        if mode == GreenletModes.RPC_SERVER:
            rpc_server_manager(daemon_id, context, sock_file)
    server = StreamServer(('0.0.0.0', conf.hub_port), handle)
    server.start()
    # wait for end or exception
    handle.catch_issues()

