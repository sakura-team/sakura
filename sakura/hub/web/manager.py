import bottle
from contextlib import contextmanager
from sakura.common.tools import JSON_PROTOCOL, WSOCK_PICKLE
from sakura.common.io import APIEndpoint
from sakura.hub.web.api import GuiToHubAPI
from sakura.hub.db import db_session_wrapper
from sakura.hub.context import greenlet_env
from sakura.common.errors import APIRequestError, APIInvalidRequest

# Turn the websocket into a file-like object.
class FileWSock(object):
    def __init__(self, wsock):
        self.wsock = wsock
    def write(self, s):
        self.wsock.send(s)
    def read(self):
        msg = self.wsock.receive()
        if msg is None:
            raise EOFError
        return msg
    def flush(self):
        pass
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

def handle_login_info(context, wsock):
    auth_kind = wsock.receive()
    if auth_kind == 'Anonymous':
        wsock.send('OK')
        return True
    elif auth_kind == 'Login':
        login_name = wsock.receive()
        password_hash = wsock.receive()
        context.login(login_name, password_hash)
        wsock.send('OK')
        return True
    else:
        print('Missing login information on /api-websocket.')
        wsock.close()
        return False

def rpc_manager(context, wsock, proto_name):
    print('New GUI RPC connection.')
    if bottle.request.path == '/api-websocket':
        login_ok = handle_login_info(context, wsock)
        if not login_ok:
            return
    # make wsock a file-like object
    f = FileWSock(wsock)
    # manage api requests
    local_api = GuiToHubAPI(context)
    web_session_wrapper = get_web_session_wrapper(context.session.id)
    protocol = { 'json': JSON_PROTOCOL,
                 'pickle': WSOCK_PICKLE }.get(proto_name)
    if protocol is None:
        print('Invalid protocol.')
    else:
        handler = APIEndpoint(f, protocol, local_api,
                    session_wrapper = web_session_wrapper)
        context.session.num_ws += 1
        try:
            handler.loop()
        except BaseException as e:
            print(e)
            pass    # hub must stay alive
    context.session.num_ws -= 1
    print('GUI RPC disconnected.')

