from sakura.client.apiobject.base import APIObjectBase
from sakura.common.errors import APIRequestError

class APIMisc:
    def __new__(cls, remote_api):
        class APIMiscImpl(APIObjectBase):
            """Sakura miscellaneous features"""
            def list_code_revisions(self, repo_url, reference=None):
                """List code revisions available from a git repository URL"""
                opts = {}
                if reference is not None:
                    if reference.__class__.__name__ == 'APIOperatorImpl':
                        opts = dict(reference_op_id = reference.op_id)
                    elif reference.__class__.__name__ == 'APIOpClassImpl':
                        opts = dict(reference_cls_id = reference.id)
                    else:
                        raise APIRequestError('list_code_revisions() expects an operator class or instance as a reference.')
                return remote_api.misc.list_code_revisions(repo_url, **opts)
            def list_operator_subdirs(self, repo_url, code_ref):
                """List repository subdirs defining an operator class"""
                return remote_api.misc.list_operator_subdirs(repo_url, code_ref)
        return APIMiscImpl()

def get_misc(remote_api):
    return APIMisc(remote_api)
