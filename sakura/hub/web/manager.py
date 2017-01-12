import json, collections
from sakura.common.wsapi import LocalAPIHandler
from sakura.hub.web.api import GuiToHubAPI

# the GUI passes a callback ID when issuing a request,
# and expects this ID to be returned with the result.
# we have to specialize the LocalAPIHandler for this.

ParsedGuiRequest = collections.namedtuple('ParsedGuiRequest',
                    ('cb_id', 'path', 'args', 'kwargs'))

class LocalGuiAPIHandler(LocalAPIHandler):
    def receive_request(self):
        raw_req = self.protocol.load(self.f)
        if raw_req == None:
            return None
        return ParsedGuiRequest(*raw_req)
    def send_result(self, req, res):
        self.protocol.dump((req.cb_id, res), self.f)

# caution: the object should be sent all at once,
# otherwise it will be received as several messages
# on the websocket. Thus we buffer possibly several
# writes, and send the whole buffer when we get a
# flush() call.
class FileWSock(object):
    def __init__(self, wsock):
        self.wsock = wsock
        self.msg = ''
    def write(self, s):
        self.msg += s
    def read(self):
        msg = self.wsock.receive()
        if msg == None:
            msg = ''
        return msg
    def flush(self):
        self.wsock.send(self.msg)
        self.msg = ''

def rpc_manager(context, wsock):
    print('New GUI RPC connection.')
    # make wsock a file-like object
    f = FileWSock(wsock)
    # manage api requests
    local_api = GuiToHubAPI(context)
    handler = LocalGuiAPIHandler(f, json, local_api)
    handler.loop()
    print('GUI RPC disconnected.')

