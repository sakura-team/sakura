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
                return APIOperator(remote_api, op_info)
        return APIDataflowOperatorsDictImpl()

class APIDataflow:
    _deleted = set()
    def __new__(cls, remote_api, info):
        dataflow_id = info['dataflow_id']
        remote_obj = remote_api.dataflows[dataflow_id]
        def get_remote_obj():
            if remote_obj in APIDataflow._deleted:
                raise ReferenceError('This dataflow is no longer valid! (was deleted)')
            else:
                return remote_obj
        class APIDataflowImpl(APIObjectBase):
            __doc__ = "Sakura dataflow: " + info['name']
            @property
            def operators(self):
                info = self.__buffered_get_info__()
                if 'operators' not in info:
                    raise APIObjectDeniedError('access denied')
                d = { op_info['op_id']: APIOperator(remote_api, op_info) \
                      for op_info in info['operators'] }
                return APIDataflowOperatorsDict(remote_api, self.dataflow_id, d)
            @property
            def grants(self):
                return APIGrants(get_remote_obj())
            def monitor(self):
                """Include events about this object in api.stream_events()"""
                obj_id = 'dataflows[%d]' % dataflow_id
                get_remote_obj().monitor(obj_id)
            def unmonitor(self):
                """Stop including events about this object in api.stream_events()"""
                obj_id = 'dataflows[%d]' % dataflow_id
                remote_api.events.unmonitor(obj_id)
            def delete(self):
                """Delete this dataflow"""
                get_remote_obj().delete()
                APIDataflow._deleted.add(remote_obj)
            def __get_remote_info__(self):
                info = get_remote_obj().info()
                if 'op_instances' in info:
                    info['operators'] = info['op_instances']
                    del info['op_instances']
                return info
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
