#!/usr/bin/env python3

from gevent import Greenlet
from sakura.common.tools import set_unbuffered_stdout, \
                                wait_greenlets
from sakura.daemon.loading import load_operator_classes
from sakura.daemon.tools import connect_to_hub, \
            get_daemon_id, set_daemon_id
from sakura.daemon.engine import DaemonEngine
from sakura.daemon.greenlets import \
            rpc_server_greenlet, rpc_client_greenlet

set_unbuffered_stdout()
print('Started.')

# load data, create engine
op_classes = load_operator_classes()
engine = DaemonEngine(op_classes)

# connect twice to the hub
srv_sock, srv_sock_file = connect_to_hub()
clt_sock, clt_sock_file = connect_to_hub()

# let the hub allocate a daemon id for us
daemon_id = get_daemon_id(srv_sock_file)

# let the hub know that the other connection
# comes from us too
set_daemon_id(clt_sock_file, daemon_id)

# run greenlets and wait until they end.
g1 = Greenlet.spawn(rpc_server_greenlet, srv_sock_file, engine)
g2 = Greenlet.spawn(rpc_client_greenlet, clt_sock_file, engine)
wait_greenlets(g1,g2)
print('**out**')
