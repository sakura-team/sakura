from sakura.client.apiobject.base import APIObjectBase, APIObjectRegistry
from sakura.common.errors import APIRequestError

class APIProjectPage:
    _deleted = set()
    def __new__(cls, remote_api, page_id):
        remote_obj = remote_api.pages[page_id]
        def get_remote_obj():
            if remote_obj in APIProjectPage._deleted:
                raise ReferenceError('Remote object was deleted!')
            else:
                return remote_obj
        class APIProjectPageImpl(APIObjectBase):
            __doc__ = 'Sakura Project Page'
            def delete(self):
                """Delete this project page"""
                get_remote_obj().delete()
                APIProjectPage._deleted.add(remote_obj)
            def update(self, page_name=None, page_content=None):
                """Update page name or content"""
                get_remote_obj().update(page_name=page_name, page_content=page_content)
            def __get_remote_info__(self):
                return get_remote_obj().info()
        return APIProjectPageImpl()
