
from gevent.server import StreamServer
from sakura.hub.daemons.manager import daemon_manager
from sakura.hub.tools import monitored

def daemons_greenlet(context):
    @monitored
    def handle(socket, address):
        daemon_id = context.get_daemon_id()
        sock_file = socket.makefile(mode='rwb')
        daemon_manager(daemon_id, context, sock_file)
    server = StreamServer(('0.0.0.0', 1234), handle)
    server.start()
    # wait for end or exception
    handle.catch_issues()

