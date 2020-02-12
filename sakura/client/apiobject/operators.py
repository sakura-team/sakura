from sakura.client.apiobject.plugs import APIOperatorInput, APIOperatorOutput
from sakura.client.apiobject.parameters import APIOperatorParameter
from sakura.client.apiobject.base import APIObjectBase, APIObjectRegistry
from sakura.common.errors import APIRequestError

class APIOperator:
    _deleted = set()
    def __new__(cls, remote_api, op_info):
        op_id = op_info['op_id']
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
            @property
            def inputs(self):
                return APIObjectRegistry({
                        in_id: APIOperatorInput(remote_api, op_id, in_id, in_info) \
                        for in_id, in_info in enumerate(self._getattr_or_raise('inputs'))
                }, "operator inputs")
            @property
            def outputs(self):
                return APIObjectRegistry({
                        out_id: APIOperatorOutput(remote_api, op_id, out_id, out_info) \
                        for out_id, out_info in enumerate(self._getattr_or_raise('outputs'))
                }, "operator outputs")
            @property
            def parameters(self):
                return APIObjectRegistry({
                        param_id: APIOperatorParameter(remote_api, op_id, param_id, param_info) \
                        for param_id, param_info in enumerate(self._getattr_or_raise('parameters'))
                }, "operator parameters")
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
            def monitor(self):
                """Include events about this object in api.stream_events()"""
                obj_id = 'operators[%d]' % op_id
                get_remote_obj().monitor(obj_id)
            def unmonitor(self):
                """Stop including events about this object in api.stream_events()"""
                obj_id = 'operators[%d]' % op_id
                remote_api.events.unmonitor(obj_id)
        return APIOperatorImpl()
