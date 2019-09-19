from gevent import Greenlet
from sakura.client import conf
from sakura.client.apiobject.opclasses import get_op_classes
from sakura.client.apiobject.dataflows import get_dataflows
from sakura.client.apiobject.databases import get_databases
from sakura.client.apiobject.misc import get_misc
from sakura.client.apiobject.base import APIObjectBase
from sakura.common.io import APIEndpoint
from sakura.common.tools import JSON_PROTOCOL

class APIRoot:
    proxy = None
    endpoint_greenlet = None
    def __new__(cls, ws):
        def init_proxy():
            endpoint = APIEndpoint(ws, JSON_PROTOCOL, None)
            APIRoot.proxy = endpoint.proxy
            APIRoot.endpoint_greenlet = Greenlet.spawn(endpoint.loop)
        def login():
            APIRoot.proxy.login(conf.username, conf.password_hash)
        ws.on_connect.subscribe(login)
        def get_proxy():
            if APIRoot.proxy is None:
                init_proxy()
            return APIRoot.proxy
        class APIRootImpl(APIObjectBase):
            "Sakura API root"
            @property
            def __ap__(self):
                return get_proxy()
            @property
            def op_classes(self):
                return get_op_classes(get_proxy())
            @property
            def dataflows(self):
                return get_dataflows(get_proxy())
            @property
            def databases(self):
                return get_databases(get_proxy())
            @property
            def misc(self):
                return get_misc(get_proxy())
            def _close(self):
                if APIRoot.proxy is not None:
                    ws.close()
                    APIRoot.endpoint_greenlet.kill()
            def set_auto_reconnect(self, value=True):
                """Indicate how this api object should act in case of disconnection from hub."""
                ws.set_auto_reconnect(value)
            def is_connected(self):
                """Indicate whether this api object is connected to hub."""
                return not ws.closed
        return APIRootImpl()
