#!/usr/bin/env python
import cPickle as pickle
from common.wsapi import LocalAPIHandler
from hub.daemons.api import DaemonToHubAPI

def daemon_manager(daemon_id, context, wsock):
    print 'daemon connected.'
    local_api = DaemonToHubAPI(daemon_id, context)
    handler = LocalAPIHandler(wsock, pickle, local_api)
    handler.loop()
    print 'daemon disconnected.'

