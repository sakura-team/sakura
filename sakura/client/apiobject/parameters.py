from sakura.client.apiobject.base import APIObjectBase
from sakura.client.apiobject.observable import APIObservableEvent

class APIOperatorParameter:
    _known = {}
    def __new__(cls, remote_api, op_activate_events, op_id, param_id, param_info):
        if (op_id, param_id) not in APIOperatorParameter._known:
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
                @property
                def on_change(self):
                    if not hasattr(self, '_on_change'):
                        self._on_change = APIObservableEvent()
                        op_activate_events()
                    return self._on_change
            APIOperatorParameter._known[(op_id, param_id)] = APIOperatorParameterImpl()
        return APIOperatorParameter._known[(op_id, param_id)]
