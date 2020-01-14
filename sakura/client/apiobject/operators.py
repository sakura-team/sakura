from sakura.client.apiobject.plugs import APIOperatorInput, APIOperatorOutput
from sakura.client.apiobject.parameters import APIOperatorParameter
from sakura.client.apiobject.base import APIObjectBase, APIObjectRegistry
from sakura.client.apiobject.events import stream_events
from sakura.common.errors import APIRequestError

class APIOperator:
    _deleted = set()
    def __new__(cls, remote_api, op_id):
        remote_obj = remote_api.operators[op_id]
        cls_name = remote_obj.info()['cls_name']
        def get_remote_obj():
            if remote_obj in APIOperator._deleted:
                raise ReferenceError('Remote object was deleted!')
            else:
                return remote_obj
        def check_online():
            if not get_remote_obj().info()['enabled']:
                raise APIRequestError('Operator is offline!')
        class APIOperatorImpl(APIObjectBase):
            __doc__ = 'Sakura ' + cls_name + ' Operator'
            @property
            def inputs(self):
                check_online()
                return APIObjectRegistry({
                        in_id: APIOperatorInput(remote_api, op_id, in_id) \
                        for in_id in range(len(get_remote_obj().info()['inputs']))
                }, "operator inputs")
            @property
            def outputs(self):
                check_online()
                return APIObjectRegistry({
                        out_id: APIOperatorOutput(remote_api, op_id, out_id) \
                        for out_id in range(len(get_remote_obj().info()['outputs']))
                }, "operator outputs")
            @property
            def parameters(self):
                check_online()
                return APIObjectRegistry({
                        param_id: APIOperatorParameter(remote_api, op_id, param_id) \
                        for param_id in range(len(get_remote_obj().info()['parameters']))
                }, "operator parameters")
            def delete(self):
                """Delete this operator"""
                check_online()
                get_remote_obj().delete()
                APIOperator._deleted.add(remote_obj)
            def reload(self):
                """Reload this operator"""
                get_remote_obj().reload()
            def update_revision(self, code_ref, commit_hash, all_ops_of_cls=False):
                """Update code revision of the operator"""
                check_online()
                remote_obj.update_revision(code_ref, commit_hash, all_ops_of_cls)
            def stream_events(self):
                """Stream events occurring on this operator"""
                yield from stream_events(get_remote_obj)
            def __doc_attrs__(self):
                return get_remote_obj().info().items()
            def __getattr__(self, attr):
                info = get_remote_obj().info()
                if attr in info:
                    return info[attr]
                else:
                    raise AttributeError('No such attribute "%s"' % attr)
        return APIOperatorImpl()
