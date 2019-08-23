from contextlib import contextmanager
from sakura.common.tools import JSON_PROTOCOL
from sakura.common.io import APIEndpoint
from sakura.hub.web.api import GuiToHubAPI
from sakura.hub.db import db_session_wrapper
from sakura.hub.context import greenlet_env
from sakura.common.errors import APIRequestError, APIInvalidRequest

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
        if len(self.msg) > 0:
            self.wsock.send(self.msg)
            self.msg = ''
    @property
    def closed(self):
        return self.wsock.closed
    def close(self):
        print('closing ws')
        self.wsock.close()

def get_web_session_wrapper(session_id):
    @contextmanager
    def web_session_wrapper():
        # record session id --
        # We cannot simply record the session object itself,
        # because it is a pony db object
        # thus its scope is limited to a db session.
        # And for each call, we get a different db session.
        greenlet_env.session_id = session_id
        # call db session wrapper
        with db_session_wrapper():
            yield
    return web_session_wrapper

def rpc_manager(context, wsock):
    print('New GUI RPC connection.')
    # make wsock a file-like object
    f = FileWSock(wsock)
    # manage api requests
    local_api = GuiToHubAPI(context)
    web_session_wrapper = get_web_session_wrapper(context.session.id)
    handler = APIEndpoint(f, JSON_PROTOCOL, local_api,
                session_wrapper = web_session_wrapper)
    context.session.num_ws += 1
    try:
        handler.loop()
    except BaseException as e:
        print(e)
        pass    # hub must stay alive
    context.session.num_ws -= 1
    print('GUI RPC disconnected.')

