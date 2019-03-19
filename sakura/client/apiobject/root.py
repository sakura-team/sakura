from sakura.client.apiobject.opclasses import get_op_classes
from sakura.client.apiobject.dataflows import get_dataflows
from sakura.client.apiobject.databases import get_databases
from sakura.client.apiobject.misc import get_misc
from sakura.client.apiobject.base import APIObjectBase

class APIRoot:
    def __new__(cls, remote_api, ws):
        class APIRootImpl(APIObjectBase):
            "Sakura API root"
            @property
            def __ap__(self):
                return remote_api
            @property
            def op_classes(self):
                return get_op_classes(remote_api)
            @property
            def dataflows(self):
                return get_dataflows(remote_api)
            @property
            def databases(self):
                return get_databases(remote_api)
            @property
            def misc(self):
                return get_misc(remote_api)
            def _close(self):
                ws.close()
        return APIRootImpl()
