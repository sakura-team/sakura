from gevent.socket import create_connection
import sakura.daemon.conf as conf

def connect_to_hub():
    sock = create_connection((conf.hub_host, conf.hub_port))
    sock_file = sock.makefile(mode='rwb')
    return sock_file
