from sakura.common.errors import APIObjectDeniedError
from sakura.client.apiobject.operators import APIOperator
from sakura.client.apiobject.base import APIObjectBase, APIObjectRegistryClass
from sakura.client.apiobject.grants import APIGrants
from sakura.common.streams import LOCAL_STREAMS

class APIDataflowOperatorsDict:
    def __new__(cls, remote_api, dataflow_id, d):
        class APIDataflowOperatorsDictImpl(APIObjectRegistryClass(d)):
            """Sakura operators registry for this dataflow"""
            def create(self, op_class):
                """Create a new operator of specified class"""
                op_info = remote_api.operators.create(dataflow_id, op_class.id, local_streams=LOCAL_STREAMS)
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
                      for op_info in self.__getattr__('op_instances') }
                return APIDataflowOperatorsDict(remote_api, self.dataflow_id, d)
            @property
            def grants(self):
                return APIGrants(remote_obj)
            def monitor(self):
                """Include events about this object in api.stream_events()"""
                obj_id = 'dataflows[%d]' % dataflow_id
                get_remote_obj().monitor(obj_id)
            def unmonitor(self):
                """Stop including events about this object in api.stream_events()"""
                obj_id = 'dataflows[%d]' % dataflow_id
                remote_api.events.unmonitor(obj_id)
            def __doc_attrs__(self):
                return info.items()
            def __getattr__(self, attr):
                info = remote_obj.info()
                if attr in info:
                    return info[attr]
                if attr == 'op_instances':
                    raise APIObjectDeniedError('access denied')
                raise AttributeError('No such attribute "%s"' % attr)
        return APIDataflowImpl()

class APIDataflowDict:
    def __new__(cls, remote_api, d):
        class APIDataflowDictImpl(APIObjectRegistryClass(d)):
            """Sakura dataflows registry"""
            def create(self, name):
                """Create a new dataflow"""
                dataflow_id = remote_api.dataflows.create(name = name)
                info = remote_api.dataflows[dataflow_id].info()
                return APIDataflow(remote_api, info)
        return APIDataflowDictImpl()

def get_dataflows(remote_api):
    d = { remote_dataflow_info['dataflow_id']: APIDataflow(remote_api, remote_dataflow_info) \
                for remote_dataflow_info in remote_api.dataflows.list() }
    return APIDataflowDict(remote_api, d)
