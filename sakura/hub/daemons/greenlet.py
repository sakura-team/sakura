
from gevent.server import StreamServer
from sakura.hub.daemons.manager import rpc_client_manager
from sakura.hub.tools import monitored
from enum import Enum

GreenletModes = Enum('GreenletModes', 'RPC_CLIENT EVENTS')

def daemons_greenlet(context):
    @monitored
    def handle(socket, address):
        sock_file = socket.makefile(mode='rwb')
        mode, daemon_id = None, None
        while True:
            req = sock_file.readline().strip()
            if req == b'GETID':
                daemon_id = context.get_daemon_id()
                sock_file.write(b'%d\n' % daemon_id)
                sock_file.flush()
            elif req == b'SETID':
                daemon_id = int(sock_file.readline().strip())
            elif req == b'RPC_SERVER':
                # if the remote end says 'server', we are client :)
                mode = GreenletModes.RPC_CLIENT
                break
        print(mode, daemon_id)
        if mode == GreenletModes.RPC_CLIENT:
            rpc_client_manager(daemon_id, context, sock_file)
    server = StreamServer(('0.0.0.0', 1234), handle)
    server.start()
    # wait for end or exception
    handle.catch_issues()

