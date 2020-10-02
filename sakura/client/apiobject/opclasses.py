from sakura.client.apiobject.operators import APIOperator
from sakura.client.apiobject.base import APIObjectBase, APIObjectRegistryClass
from sakura.client.apiobject.grants import APIGrants
from sakura.common.tools import create_names_dict, camelcase

class APIOpClass:
    _deleted = set()
    def __new__(cls, remote_api, info):
        cls_id = info['id']
        remote_obj = remote_api.op_classes[cls_id]
        def get_remote_obj():
            if remote_obj in APIOpClass._deleted:
                raise ReferenceError('This class is no longer valid! (was unregistered)')
            else:
                return remote_obj
        class APIOpClassImpl(APIObjectBase):
            __doc__ = 'Sakura ' + info['name'] + ' Operator Class'
            def __get_remote_info__(self):
                return get_remote_obj().info()
            @property
            def grants(self):
                return APIGrants(get_remote_obj())
            def update_default_revision(self, code_ref, commit_hash):
                """Update default code revision of this operator class"""
                return get_remote_obj().update_default_revision(code_ref, commit_hash)
            def unregister(self):
                """Unregister this operator class"""
                get_remote_obj().unregister()
                APIOpClass._deleted.add(remote_obj)
            def create(self, dataflow):
                """Create a new operator of this class in specified dataflow"""
                op_info = remote_api.operators.create(dataflow.dataflow_id, cls_id)
                op_id = op_info['op_id']
                return APIOperator(remote_api, op_id)
        return APIOpClassImpl()

class APIOpClassDict:
    def __new__(cls, remote_api, d):
        class APIOpClassDictImpl(APIObjectRegistryClass(d)):
            """Sakura operator classes registry"""
            def register_from_git_repo(self, repo_url, default_code_ref, default_commit_hash, repo_subdir='/', access_scope='public'):
                """Registration of a new operator class from a git repository"""
                return self.register(
                        repo_type = 'git',
                        repo_url = repo_url,
                        default_code_ref = default_code_ref,
                        default_commit_hash = default_commit_hash,
                        repo_subdir = repo_subdir,
                        access_scope = access_scope
                )
            def register_from_sandbox(self, sandbox_uuid, sandbox_dir, sandbox_streams, repo_subdir='/'):
                """Registration of a new operator class from a sandbox process"""
                return self.register(
                        repo_type = 'sandbox',
                        sandbox_uuid = sandbox_uuid,
                        sandbox_dir = sandbox_dir,
                        sandbox_streams = sandbox_streams,
                        repo_subdir = repo_subdir,
                        access_scope = 'private'
                )
            def register(self, **kwargs):
                """Registration of a new operator class (generic procedure)"""
                cls_info = remote_api.op_classes.register(**kwargs)
                return APIOpClass(remote_api, cls_info)
        return APIOpClassDictImpl()

def get_op_classes(remote_api):
    d = create_names_dict(
        ((remote_op_cls_info['name'], APIOpClass(remote_api, remote_op_cls_info)) \
         for remote_op_cls_info in remote_api.op_classes.list()),
        name_format = camelcase
    )
    return APIOpClassDict(remote_api, d)
