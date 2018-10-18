from sakura.client.apiobject.operators import APIOperator

class APIOpClass:
    def __new__(cls, remote_api, cls_id):
        remote_obj = remote_api.op_classes[cls_id]
        class APIOpClassImpl:
            def __getattr__(self, attr):
                info = remote_obj.info()
                if attr in info:
                    return info[attr]
                else:
                    raise AttributeError('No such attribute "%s"' % attr)
            def __call__(self, dataflow):
                op_info = remote_api.operators.create(dataflow.dataflow_id, cls_id)
                op_id = op_info['op_id']
                return APIOperator(remote_api, op_id)
            def __repr__(self):
                return '<Sakura ' + self.name + ' Operator Class>'
        return APIOpClassImpl()

def get_op_classes(remote_api):
    return { remote_op_cls_info['name']: APIOpClass(remote_api, remote_op_cls_info['id']) \
                for remote_op_cls_info in remote_api.op_classes.list() }
