from sakura.client.apiobject.plugs import APIOperatorInput, APIOperatorOutput

class APIOperator:
    _deleted = set()
    def __new__(cls, remote_api, op_id):
        remote_obj = remote_api.operators[op_id]
        def get_remote_obj():
            if remote_obj in APIOperator._deleted:
                raise ReferenceError('Remote object was deleted!')
            else:
                return remote_obj
        class APIOperatorImpl:
            @property
            def inputs(self):
                return {
                    in_info['label']: APIOperatorInput(remote_api, op_id, in_id) \
                        for in_id, in_info in enumerate(get_remote_obj().info()['inputs'])
                }
            @property
            def outputs(self):
                return {
                    out_info['label']: APIOperatorOutput(remote_api, op_id, out_id) \
                        for out_id, out_info in enumerate(get_remote_obj().info()['outputs'])
                }
            def delete(self):
                get_remote_obj().delete()
                APIOperator._deleted.add(remote_obj)
            def __getattr__(self, attr):
                info = get_remote_obj().info()
                if attr in info:
                    return info[attr]
                else:
                    raise AttributeError('No such attribute "%s"' % attr)
            def __repr__(self):
                return '<Sakura ' + self.cls_name + ' Operator>'
        return APIOperatorImpl()
