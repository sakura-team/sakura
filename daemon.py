#!/usr/bin/env python3

import pickle
from gevent.socket import create_connection
#from gevent import monkey
#monkey.patch_all()
from common.wsapi import get_remote_api, LocalAPIHandler
from daemon.init import init_connexion_to_hub
from daemon.api import HubToDaemonAPI

sock = create_connection(('localhost', 1234))
sock_file = sock.makefile(mode='rwb')

remote_api = get_remote_api(sock_file, pickle)
local_api = HubToDaemonAPI()

init_connexion_to_hub(remote_api)
handler = LocalAPIHandler(sock_file, pickle, local_api)
handler.loop()

sock_file.close()
sock.close()
