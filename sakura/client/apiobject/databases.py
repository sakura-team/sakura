from sakura.common.errors import APIObjectDeniedError
from sakura.client.apiobject.base import APIObjectBase, APIObjectRegistry
from sakura.client.apiobject.tables import APITable
from sakura.client.apiobject.grants import APIGrants

class APIDatabaseTablesDict:
    def __new__(cls, remote_api, database_id, d):
        class APIDatabaseTablesDictImpl(APIObjectRegistry(d)):
            """Sakura tables registry for this database"""
        return APIDatabaseTablesDictImpl()

class APIDatabase:
    def __new__(cls, remote_api, db_id):
        remote_obj = remote_api.databases[db_id]
        def get_info():
            return remote_obj.info()
        class APIDatabaseImpl(APIObjectBase):
            __doc__ = 'Sakura Database: ' + get_info()['name']
            @property
            def tables(self):
                d = { table_info['table_id']: APITable(remote_api, table_info['table_id']) \
                      for table_info in self.__getattr__('tables') }
                return APIDatabaseTablesDict(remote_api, self.database_id, d)
            @property
            def grants(self):
                return APIGrants(remote_obj)
            def __doc_attrs__(self):
                return get_info().items()
            def __getattr__(self, attr):
                info = get_info()
                if attr in info:
                    return info[attr]
                if attr == 'tables':
                    raise APIObjectDeniedError('access denied')
                raise AttributeError('No such attribute "%s"' % attr)
        return APIDatabaseImpl()

class APIDatabaseDict:
    def __new__(cls, remote_api, d):
        class APIDatabaseDictImpl(APIObjectRegistry(d)):
            """Sakura databases registry"""
        return APIDatabaseDictImpl()

def get_databases(remote_api):
    d = { remote_db_info['database_id']: APIDatabase(remote_api, remote_db_info['database_id']) \
                for remote_db_info in remote_api.databases.list() }
    return APIDatabaseDict(remote_api, d)
