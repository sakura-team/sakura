#!/usr/bin/env python
import json
from common.wsapi import LocalAPIHandler
from hub.gui.api import GuiToHubAPI

def gui_manager(context, wsock):
    print 'GUI connected.'
    local_api = GuiToHubAPI(context)
    handler = LocalAPIHandler(wsock, json, local_api)
    handler.loop()
    print 'GUI disconnected.'

