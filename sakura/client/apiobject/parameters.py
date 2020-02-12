from sakura.client.apiobject.base import APIObjectBase

class APIOperatorParameter:
    def __new__(cls, remote_api, op_id, param_id, param_info):
        remote_op = remote_api.operators[op_id]
        def get_info():
            return remote_op.info()['parameters'][param_id]
        class APIOperatorParameterImpl(APIObjectBase):
            __doc__ = 'Sakura parameter: ' + param_info['label']
            def __get_remote_info__(self):
                return remote_op.info()['parameters'][param_id]
            def set_value(self, value):
                """Set parameter value"""
                remote_api.operators[op_id].parameters[param_id].set_value(value)
        return APIOperatorParameterImpl()
