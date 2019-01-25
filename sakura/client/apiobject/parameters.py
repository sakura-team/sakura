from sakura.client.apiobject.base import APIObjectBase

class APIOperatorParameter:
    def __new__(cls, remote_api, op_id, param_id):
        remote_op = remote_api.operators[op_id]
        def get_info():
            return remote_op.info()['parameters'][param_id]
        class APIOperatorParameterImpl(APIObjectBase):
            __doc__ = 'Sakura parameter: ' + get_info()['label']
            def __doc_attrs__(self):
                return get_info().items()
            def __getattr__(self, attr):
                info = get_info()
                if attr in info:
                    return info[attr]
                else:
                    raise AttributeError('No such attribute "%s"' % attr)
            def set_value(self, value):
                """Set parameter value"""
                remote_api.operators[op_id].parameters[param_id].set_value(value)
        return APIOperatorParameterImpl()
