from sakura.client.apiobject.plugs import APIOperatorInput, APIOperatorOutput
from sakura.client.apiobject.parameters import APIOperatorParameter
from sakura.client.apiobject.base import APIObjectBase

class APIOperator:
    _deleted = set()
    def __new__(cls, remote_api, op_id):
        remote_obj = remote_api.operators[op_id]
        def get_remote_obj():
            if remote_obj in APIOperator._deleted:
                raise ReferenceError('Remote object was deleted!')
            else:
                return remote_obj
        class APIOperatorImpl(APIObjectBase):
            __doc__ = 'Sakura ' + remote_obj.info()['cls_name'] + ' Operator'
            @property
            def inputs(self):
                return [ APIOperatorInput(remote_api, op_id, in_id) \
                         for in_id in range(len(get_remote_obj().info()['inputs']))
                ]
            @property
            def outputs(self):
                return [ APIOperatorOutput(remote_api, op_id, out_id) \
                        for out_id in range(len(get_remote_obj().info()['outputs']))
                ]
            @property
            def parameters(self):
                return [ APIOperatorParameter(remote_api, op_id, param_id) \
                        for param_id in range(len(get_remote_obj().info()['parameters']))
                ]
            def delete(self):
                """Delete this operator"""
                get_remote_obj().delete()
                APIOperator._deleted.add(remote_obj)
            def __doc_attrs__(self):
                return get_remote_obj().info().items()
            def __getattr__(self, attr):
                info = get_remote_obj().info()
                if attr in info:
                    return info[attr]
                else:
                    raise AttributeError('No such attribute "%s"' % attr)
        return APIOperatorImpl()
