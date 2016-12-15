
from gevent.server import StreamServer
from hub.daemons.manager import daemon_manager

def daemons_greenlet(context):
    def handle(socket, address):
        daemon_id = context.get_daemon_id()
        sock_file = socket.makefile(mode='rwb')
        daemon_manager(daemon_id, context, sock_file)
    server = StreamServer(('0.0.0.0', 1234), handle)
    server.start() # start accepting new connections

