from sakura.client.apiobject.plugs import APIOperatorInput, APIOperatorOutput
from sakura.client.apiobject.parameters import APIOperatorParameter
from sakura.client.apiobject.observable import APIObservableEvent
from sakura.client.apiobject.base import APIObjectBase, APIObjectRegistry
from sakura.client.events import set_event_callback
from sakura.common.errors import APIRequestError
from sakura.common.tools import create_names_dict, snakecase

class APIOperator:
    _known = {}
    _deleted = set()
    def __new__(cls, remote_api, op_info):
        op_id = op_info['op_id']
        if op_id not in APIOperator._known:
            remote_obj = remote_api.operators[op_id]
            cls_name = op_info['cls_name']
            def get_remote_obj():
                if remote_obj in APIOperator._deleted:
                    raise ReferenceError('Remote object was deleted!')
                else:
                    return remote_obj
            class APIOperatorImpl(APIObjectBase):
                __doc__ = 'Sakura ' + cls_name + ' Operator'
                def _check_online(self):
                    if not self.enabled:
                        raise APIRequestError('Operator is offline!')
                def _getattr_or_raise(self, attr):
                    try:
                        return self.__getattr__(attr)
                    except AttributeError:
                        if not self.enabled:
                            raise APIRequestError('Operator is offline!')
                        raise
                def __get_remote_info__(self):
                    return get_remote_obj().info()
                def _activate_events(self):
                    events_obj_id = 'operators[' + str(op_id) + ']'
                    if not getattr(self, '_events_activated', False):
                        get_remote_obj().monitor(events_obj_id)
                        set_event_callback(remote_api, events_obj_id, self._events_cb)
                        self._events_activated = True
                def _get_sub_object(self, objset, idx):
                    obj_info = tuple(self._getattr_or_raise(objset))[idx]
                    for subobj in getattr(self, objset).values():
                        if subobj.label == obj_info['label']:
                            return subobj
                def _events_cb(self, evt_name, *evt_args, **evt_kwargs):
                    observable = None
                    if evt_name == 'enabled':
                        observable = self.on_enabled
                    elif evt_name == 'disabled':
                        observable = self.on_disabled
                    elif evt_name == 'altered_parameter':
                        idx = evt_args[0]
                        observable = self._get_sub_object('parameters', idx).on_change
                    elif evt_name == 'altered_input':
                        idx = evt_args[0]
                        observable = self._get_sub_object('inputs', idx).on_change
                    elif evt_name == 'altered_output':
                        idx = evt_args[0]
                        observable = self._get_sub_object('outputs', idx).on_change
                    # note: other events are ignored
                    if observable is not None:
                        observable.notify()
                @property
                def on_enabled(self):
                    if not hasattr(self, '_on_enabled'):
                        self._on_enabled = APIObservableEvent()
                        self._activate_events()
                    return self._on_enabled
                @property
                def on_disabled(self):
                    if not hasattr(self, '_on_disabled'):
                        self._on_disabled = APIObservableEvent()
                        self._activate_events()
                    return self._on_disabled
                @property
                def inputs(self):
                    return APIObjectRegistry(create_names_dict(
                        ((in_info['label'], APIOperatorInput(remote_api, self._activate_events, op_id, in_id, in_info)) \
                         for in_id, in_info in enumerate(self._getattr_or_raise('inputs'))),
                        name_format = snakecase
                    ), "operator inputs")
                @property
                def outputs(self):
                    return APIObjectRegistry(create_names_dict(
                        ((out_info['label'], APIOperatorOutput(remote_api, self._activate_events, op_id, out_id, out_info)) \
                         for out_id, out_info in enumerate(self._getattr_or_raise('outputs'))),
                        name_format = snakecase
                    ), "operator outputs")
                @property
                def parameters(self):
                    return APIObjectRegistry(create_names_dict(
                        ((param_info['label'], APIOperatorParameter(remote_api, self._activate_events, op_id, param_id, param_info)) \
                         for param_id, param_info in enumerate(self._getattr_or_raise('parameters'))),
                        name_format = snakecase
                    ), "operator parameters")
                def delete(self):
                    """Delete this operator"""
                    self._check_online()
                    get_remote_obj().delete()
                    APIOperator._deleted.add(remote_obj)
                def reload(self):
                    """Reload this operator"""
                    get_remote_obj().reload()
                def update_revision(self, code_ref, commit_hash, all_ops_of_cls=False):
                    """Update code revision of the operator"""
                    self._check_online()
                    remote_obj.update_revision(code_ref, commit_hash, all_ops_of_cls)
            APIOperator._known[op_id] = APIOperatorImpl()
        return APIOperator._known[op_id]
