from sakura.client import conf
from sakura.client.apiobject.opclasses import get_op_classes
from sakura.client.apiobject.dataflows import get_dataflows
from sakura.client.apiobject.projects import get_projects
from sakura.client.apiobject.databases import get_databases
from sakura.client.apiobject.datastores import get_datastores
from sakura.client.apiobject.users import get_users
from sakura.client.apiobject.misc import get_misc
from sakura.client.apiobject.base import APIObjectBase

class APIRoot:
    def __new__(cls, ws):
        class APIRootImpl(APIObjectBase):
            "Sakura API root"
            @property
            def __ap__(self):
                return ws.proxy
            @property
            def projects(self):
                return get_projects(ws.proxy)
            @property
            def op_classes(self):
                return get_op_classes(ws.proxy)
            @property
            def dataflows(self):
                return get_dataflows(ws.proxy)
            @property
            def datastores(self):
                return get_datastores(ws.proxy)
            @property
            def databases(self):
                return get_databases(ws.proxy)
            @property
            def users(self):
                return get_users(ws.proxy)
            @property
            def misc(self):
                return get_misc(ws.proxy)
            def _close(self):
                ws.close()
            def is_connected(self):
                """Indicate whether this api object is connected to hub."""
                return not ws.closed
            def check(self):
                """Ensure this api object is properly configured."""
                conf.check(ws.proxy, ws.set_connect_timeout)
        return APIRootImpl()
