import collections, json, numpy as np
from contextlib import contextmanager
from sakura.common.io import LocalAPIHandler
from sakura.hub.web.api import GuiToHubAPI
from sakura.hub.db import db_session_wrapper
from sakura.hub.context import greenlet_env
from sakura.common.errors import APIRequestError

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

def gui_fallback_handler(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, type) and hasattr(obj, 'select'):    # for pony entities
        return tuple(o for o in obj.select())
    elif hasattr(obj, 'pack'):
        return obj.pack()
    elif hasattr(obj, '_asdict'):
        return obj._asdict()
    elif hasattr(obj, '__iter__'):
        return tuple(o for o in obj)
    elif hasattr(obj, 'item'):
        return obj.item()   # convert numpy scalar to native
    else:
        raise Exception('Dont know how to serialize "' + repr(obj) + \
                    '" class=' + repr(obj.__class__))

class GUILocalAPIProtocol:
    @staticmethod
    def load(f):
        return json.load(f)
    @staticmethod
    def dump(res_info, f):
        try:
            # json.dump() function causes performance issues
            # because it performs many small writes on f.
            # So we json-encode in a string (json.dumps)
            # and then write this whole string at once.
            res_json = json.dumps(res_info,
                separators=(',', ':'),
                default=gui_fallback_handler)
            f.write(res_json)
        except BaseException as e:
            print(e)
            raise Exception('Hub->GUI: Hub could not serialize object ' + \
                                repr(res_info))

def rpc_manager(context, wsock, session):
    print('New GUI RPC connection.')
    # make wsock a file-like object
    f = FileWSock(wsock)
    # manage api requests
    local_api = GuiToHubAPI(context)
    web_session_wrapper = get_web_session_wrapper(session.id)
    handler = LocalAPIHandler(f, GUILocalAPIProtocol, local_api,
                session_wrapper = web_session_wrapper)
    session.num_ws += 1
    handler.loop()
    session.num_ws -= 1
    print('GUI RPC disconnected.')

