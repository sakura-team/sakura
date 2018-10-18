from sakura.client.apiobject.operators import APIOperator

class APIDataflow:
    def __new__(cls, remote_api, info):
        dataflow_id = info['dataflow_id']
        remote_obj = remote_api.dataflows[dataflow_id]
        class APIDataflowImpl:
            @property
            def operators(self):
                return [
                    APIOperator(remote_api, op_info['op_id']) \
                        for op_info in remote_obj.info()['op_instances']
                ]
            def __getattr__(self, attr):
                info = remote_obj.info()
                if attr in info:
                    return info[attr]
                else:
                    raise AttributeError('No such attribute "%s"' % attr)
            def __repr__(self):
                return '<Sakura dataflow "' + self.name + '">'
        return APIDataflowImpl()

def get_dataflows(remote_api):
    return { remote_dataflow_info['name']: APIDataflow(remote_api, remote_dataflow_info) \
                for remote_dataflow_info in remote_api.dataflows.list() }
