from sakura.client.apiobject.base import APIObjectBase, APIObjectRegistry
from sakura.client import conf

class APIUser:
    _deleted = set()
    def __new__(cls, remote_api, info):
        login = info['login']
        remote_obj = remote_api.users[login]
        def get_remote_obj():
            if remote_obj in APIUser._deleted:
                raise ReferenceError('This class is no longer valid! (was unregistered)')
            else:
                return remote_obj
        def get_info():
            return get_remote_obj().info()
        class APIUserImpl(APIObjectBase):
            __doc__ = 'Sakura user "' + info['login'] + '"'
            def __doc_attrs__(self):
                return get_info().items()
            def __getattr__(self, attr):
                info = get_info()
                if attr in info:
                    return info[attr]
                else:
                    raise AttributeError('No such attribute "%s"' % attr)
        return APIUserImpl()

class APIUserDict:
    def __new__(cls, remote_api, d):
        class APIUserDictImpl(APIObjectRegistry(d)):
            """Sakura users registry"""
            def current(self):
                """return user currently logged in"""
                return self[conf.username]
        return APIUserDictImpl()

def get_users(remote_api):
    d = { remote_user_info['login']: APIUser(remote_api, remote_user_info) \
                for remote_user_info in remote_api.users.list() }
    return APIUserDict(remote_api, d)
