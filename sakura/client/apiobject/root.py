from gevent import Greenlet
from sakura.client.apiobject.opclasses import get_op_classes
from sakura.client.apiobject.dataflows import get_dataflows
from sakura.client.apiobject.databases import get_databases
from sakura.client.apiobject.misc import get_misc
from sakura.client.apiobject.base import APIObjectBase

class APIRoot:
    def __new__(cls, endpoint, ws):
        proxy = endpoint.proxy
        g = Greenlet.spawn(endpoint.loop)
        class APIRootImpl(APIObjectBase):
            "Sakura API root"
            @property
            def __ap__(self):
                return proxy
            @property
            def op_classes(self):
                return get_op_classes(proxy)
            @property
            def dataflows(self):
                return get_dataflows(proxy)
            @property
            def databases(self):
                return get_databases(proxy)
            @property
            def misc(self):
                return get_misc(proxy)
            def _close(self):
                ws.close()
                g.kill()
        return APIRootImpl()
