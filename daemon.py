#!/usr/bin/env python3

import pickle
from gevent.socket import create_connection
#from gevent import monkey
#monkey.patch_all()
from sakura.common.wsapi import LocalAPIHandler
from sakura.common.tools import set_unbuffered_stdout
from sakura.daemon.loading import load_operator_classes
from sakura.daemon.api import HubToDaemonAPI

set_unbuffered_stdout()
print('Started.')
op_classes = load_operator_classes()

sock = create_connection(('localhost', 1234))
sock_file = sock.makefile(mode='rwb')
sock_file.write(b'GETID\n')
sock_file.flush()
daemon_id = int(sock_file.readline().strip())
sock_file.write(b'RPC_SERVER\n')
sock_file.flush()

local_api = HubToDaemonAPI(op_classes)

handler = LocalAPIHandler(sock_file, pickle, local_api)
handler.loop()

sock_file.close()
sock.close()
