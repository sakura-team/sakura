from sakura.client.apiobject.base import APIObjectBase, APIObjectRegistry

class APIUserGrant:
    def __new__(cls, remote_obj, login, grant_info):
        class APIUserGrantImpl(APIObjectBase):
            """User grant"""
            def __doc_attrs__(self):
                return grant_info.items()
            def __getattr__(self, attr):
                if attr in grant_info:
                    return grant_info[attr]
                else:
                    raise AttributeError('No such attribute "%s"' % attr)
        return APIUserGrantImpl()

class APIGrants:
    def __new__(cls, remote_obj):
        d = { login: APIUserGrant(remote_obj, login, grant_info) \
              for login, grant_info in remote_obj.info()['grants'].items() }
        class APIGrantsImpl(APIObjectRegistry(d)):
            """Grants registry"""
            def update(self, login, grant_name):
                """update or add a user grant"""
                remote_obj.grants.update(login, grant_name)
            def request(self, grant_name, argumentative_text):
                """request a grant on this object"""
                remote_obj.grants.request(grant_name, argumentative_text)
        return APIGrantsImpl()
