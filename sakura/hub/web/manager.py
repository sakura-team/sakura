import collections
from sakura.common.io import LocalAPIHandler, compactjson
from sakura.hub.web.api import GuiToHubAPI
from sakura.hub.db import db_session_wrapper

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

class ResultWrapper:
    @staticmethod
    def on_success(result):
        return (True, result)
    @staticmethod
    def on_exception(exc):
        if isinstance(exc, ValueError):
            return (False, str(exc))
        else:
            raise exc

def rpc_manager(context, wsock, session):
    print('New GUI RPC connection.')
    # make wsock a file-like object
    f = FileWSock(wsock)
    # manage api requests
    local_api = GuiToHubAPI(context, session)
    handler = LocalAPIHandler(f, compactjson, local_api,
                session_wrapper = db_session_wrapper,
                result_wrapper = ResultWrapper)
    session.num_ws += 1
    handler.loop()
    session.num_ws -= 1
    print('GUI RPC disconnected.')

