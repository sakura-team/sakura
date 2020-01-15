import pickle
from gevent.server import StreamServer
from gevent.socket import IPPROTO_TCP, TCP_NODELAY
from sakura.hub.daemons.manager import rpc_manager
from sakura.common.tools import monitored
from sakura.hub import conf
from sakura.common.io.serializer import Serializer

def daemons_greenlet(context):
    @monitored
    def handle(socket, address):
        socket.setsockopt(IPPROTO_TCP, TCP_NODELAY, 1)
        sock_file = Serializer(socket.makefile(mode='rwb', buffering=0))
        daemon_name = pickle.load(sock_file)
        rpc_manager(context, daemon_name, sock_file)
    server = StreamServer(('', conf.hub_port), handle)
    server.start()
    # wait for end or exception
    handle.catch_issues()
