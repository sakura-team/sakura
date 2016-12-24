#!/usr/bin/env python3

import pickle
from gevent.socket import create_connection
#from gevent import monkey
#monkey.patch_all()
from sakura.common.wsapi import get_remote_api, LocalAPIHandler
from sakura.common.tools import set_unbuffered_stdout
from sakura.daemon.loading import load_operator_classes
from sakura.daemon.loading import init_connexion_to_hub
from sakura.daemon.api import HubToDaemonAPI

set_unbuffered_stdout()
print('Started.')
op_classes = load_operator_classes()

sock = create_connection(('localhost', 1234))
sock_file = sock.makefile(mode='rwb')

remote_api = get_remote_api(sock_file, pickle)
local_api = HubToDaemonAPI()

init_connexion_to_hub(remote_api, op_classes)
handler = LocalAPIHandler(sock_file, pickle, local_api)
handler.loop()

sock_file.close()
sock.close()
