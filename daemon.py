#!/usr/bin/env python3

import gevent, json
#from gevent import monkey
#monkey.patch_all()
from common.wsapi import get_remote_api, LocalAPIHandler, get_client_wsock
from daemon.init import init_connexion_to_hub
from daemon.api import HubToDaemonAPI
    
wsock = get_client_wsock("ws://localhost:8081/websockets/daemon")
remote_api = get_remote_api(wsock, json)
local_api = HubToDaemonAPI()

init_connexion_to_hub(remote_api)
handler = LocalAPIHandler(wsock, json, local_api)
handler.loop()

wsock.close()
