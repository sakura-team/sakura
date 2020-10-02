from sakura.common.errors import APIObjectDeniedError
from sakura.client.apiobject.base import APIObjectBase, APIObjectRegistryClass
from sakura.client.apiobject.grants import APIGrants
from sakura.client.apiobject.pages import APIProjectPage
from sakura.common.tools import create_names_dict, snakecase

class APIProjectPagesDict:
    def __new__(cls, remote_api, project_id, d):
        class APIProjectPagesDictImpl(APIObjectRegistryClass(d)):
            """Pages of this project"""
            def create(self, page_name):
                """Create a new page for this project"""
                page_id = remote_api.pages.create(project_id, page_name)
                return APIProjectPage(remote_api, page_id)
        return APIProjectPagesDictImpl()

class APIProject:
    _deleted = set()
    def __new__(cls, remote_api, info):
        project_id = info['project_id']
        remote_obj = remote_api.projects[project_id]
        def get_remote_obj():
            if remote_obj in APIProject._deleted:
                raise ReferenceError('This project is no longer valid! (was deleted)')
            else:
                return remote_obj
        class APIProjectImpl(APIObjectBase):
            __doc__ = "Sakura project: " + info['name']
            @property
            def pages(self):
                info = self.__buffered_get_info__()
                if 'pages' not in info:
                    raise APIObjectDeniedError('access denied')
                d = create_names_dict(
                    ((page_info['page_name'], APIProjectPage(remote_api, page_info['page_id'])) \
                     for page_info in info['pages']),
                    name_format = snakecase
                )
                return APIProjectPagesDict(remote_api, project_id, d)
            @property
            def grants(self):
                return APIGrants(get_remote_obj())
            def delete(self):
                """Delete this project"""
                get_remote_obj().delete()
                APIProject._deleted.add(remote_obj)
            def __get_remote_info__(self):
                return get_remote_obj().info()
        return APIProjectImpl()

class APIProjectDict:
    def __new__(cls, remote_api, d):
        class APIProjectDictImpl(APIObjectRegistryClass(d)):
            """Sakura projects registry"""
            def create(self, name):
                """Create a new project"""
                project_id = remote_api.projects.create(name = name)
                info = remote_api.projects[project_id].info()
                return APIProject(remote_api, info)
        return APIProjectDictImpl()

def get_projects(remote_api):
    d = create_names_dict(
        ((project_info['name'], APIProject(remote_api, project_info)) \
         for project_info in remote_api.projects.list()),
        name_format = snakecase
    )
    return APIProjectDict(remote_api, d)
