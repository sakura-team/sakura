#!/usr/bin/env python3

import pickle
from gevent.socket import create_connection
#from gevent import monkey
#monkey.patch_all()
from sakura.common.wsapi import LocalAPIHandler
from sakura.common.tools import set_unbuffered_stdout
from sakura.daemon.loading import load_operator_classes
from sakura.daemon.tools import get_daemon_id
from sakura.daemon.engine import DaemonEngine

set_unbuffered_stdout()
print('Started.')

# load data, create engine
op_classes = load_operator_classes()
engine = DaemonEngine(op_classes)

# connect to the hub
sock = create_connection(('localhost', 1234))
sock_file = sock.makefile(mode='rwb')

# let the hub allocate a daemon id for us
daemon_id = get_daemon_id(sock_file)

# instruct the hub to use this connection as a RPC server
sock_file.write(b'RPC_SERVER\n')
sock_file.flush()

# handle this RPC API
local_api = engine
handler = LocalAPIHandler(sock_file, pickle, local_api)
handler.loop()

# cleanup
sock_file.close()
sock.close()
