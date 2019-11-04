from sakura.client.apiobject.base import APIObjectBase, APIObjectRegistryClass
from sakura.client import conf

class APIUserPrivileges:
    def __new__(cls, remote_obj):
        class APIUserPrivilegesImpl(APIObjectBase):
            __doc__ = 'User privileges'
            @property
            def assigned(self):
                """assigned privileges"""
                return remote_obj.info()['privileges']
            @property
            def requested(self):
                """requested privileges"""
                return remote_obj.info()['requested_privileges']
            def request(self, privilege):
                """request a new privilege"""
                return remote_obj.privileges.request(privilege)
            def add(self, privilege):
                """add a privilege to this user"""
                return remote_obj.privileges.add(privilege)
            def remove(self, privilege):
                """remove a privilege from this user"""
                return remote_obj.privileges.remove(privilege)
            def deny(self, privilege):
                """deny a privilege request from this user"""
                return remote_obj.privileges.deny(privilege)
        return APIUserPrivilegesImpl()

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
                info = get_info()
                info.pop('privileges')
                info.pop('requested_privileges')
                return info.items()
            def __getattr__(self, attr):
                info = get_info()
                if attr in info:
                    return info[attr]
                else:
                    raise AttributeError('No such attribute "%s"' % attr)
            @property
            def privileges(self):
                return APIUserPrivileges(remote_obj)
        return APIUserImpl()

class APIUserDict:
    def __new__(cls, remote_api, d):
        class APIUserDictImpl(APIObjectRegistryClass(d)):
            """Sakura users registry"""
            def current(self):
                """return user currently logged in"""
                return self[conf.username]
        return APIUserDictImpl()

def get_users(remote_api):
    d = { remote_user_info['login']: APIUser(remote_api, remote_user_info) \
                for remote_user_info in remote_api.users.list() }
    return APIUserDict(remote_api, d)
