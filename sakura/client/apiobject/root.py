from sakura.client.apiobject.opclasses import get_op_classes
from sakura.client.apiobject.dataflows import get_dataflows

class APIRoot:
    def __new__(cls, remote_api, ws):
        class APIRootImpl:
            @property
            def __ap__(self):
                return remote_api
            @property
            def op_classes(self):
                return get_op_classes(remote_api)
            @property
            def dataflows(self):
                return get_dataflows(remote_api)
            def _close(self):
                ws.close()
            def __repr__(self):
                return '<Sakura client API object>'
        return APIRootImpl()
