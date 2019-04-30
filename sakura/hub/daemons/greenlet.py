import pickle
from gevent.server import StreamServer
from sakura.hub.daemons.manager import rpc_manager
from sakura.common.tools import monitored
import sakura.hub.conf as conf

def daemons_greenlet(context):
    @monitored
    def handle(socket, address):
        sock_file = socket.makefile(mode='rwb')
        daemon_name = pickle.load(sock_file)
        rpc_manager(context, daemon_name, sock_file)
    server = StreamServer(('', conf.hub_port), handle)
    server.start()
    # wait for end or exception
    handle.catch_issues()
