#!/usr/bin/env python

import gevent, cPickle as pickle
#from gevent import monkey
#monkey.patch_all()
from common.wsapi import get_remote_api, LocalAPIHandler, get_client_wsock
from daemon.init import init_connexion_to_hub
from daemon.api import HubToDaemonAPI
    
wsock = get_client_wsock("ws://localhost:8080/websockets/daemon")
remote_api = get_remote_api(wsock, pickle)
local_api = HubToDaemonAPI()

init_connexion_to_hub(remote_api)
handler = LocalAPIHandler(wsock, pickle, local_api)
handler.loop()

wsock.close()
