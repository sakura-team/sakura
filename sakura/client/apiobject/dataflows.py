from sakura.client.apiobject.operators import APIOperator
from sakura.client.apiobject.base import APIObjectBase, APIObjectRegistry

class APIDataflowOperatorsDict:
    def __new__(cls, remote_api, dataflow_id, d):
        class APIDataflowOperatorsDictImpl(APIObjectRegistry(d)):
            """Sakura operators registry for this dataflow"""
            def create(self, op_class):
                """Create a new operator of specified class"""
                op_info = remote_api.operators.create(dataflow_id, op_class.id)
                op_id = op_info['op_id']
                return APIOperator(remote_api, op_id)
        return APIDataflowOperatorsDictImpl()

class APIDataflow:
    def __new__(cls, remote_api, info):
        dataflow_id = info['dataflow_id']
        remote_obj = remote_api.dataflows[dataflow_id]
        class APIDataflowImpl(APIObjectBase):
            __doc__ = "Sakura dataflow: " + info['name']
            @property
            def operators(self):
                d = { op_info['op_id']: APIOperator(remote_api, op_info['op_id']) \
                      for op_info in remote_obj.info()['op_instances'] }
                return APIDataflowOperatorsDict(remote_api, self.dataflow_id, d)
            def __doc_attrs__(self):
                return info.items()
            def __getattr__(self, attr):
                info = remote_obj.info()
                if attr in info:
                    return info[attr]
                else:
                    raise AttributeError('No such attribute "%s"' % attr)
        return APIDataflowImpl()

class APIDataflowDict:
    def __new__(cls, remote_api, d):
        class APIDataflowDictImpl(APIObjectRegistry(d)):
            """Sakura dataflows registry"""
            def create(self, name):
                """Create a new dataflow"""
                return remote_api.dataflows.create(name = name)
        return APIDataflowDictImpl()

def get_dataflows(remote_api):
    d = { remote_dataflow_info['dataflow_id']: APIDataflow(remote_api, remote_dataflow_info) \
                for remote_dataflow_info in remote_api.dataflows.list() }
    return APIDataflowDict(remote_api, d)
