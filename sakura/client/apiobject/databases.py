from sakura.common.errors import APIObjectDeniedError
from sakura.client.apiobject.base import APIObjectBase, APIObjectRegistry
from sakura.client.apiobject.tables import APITable
from sakura.client.apiobject.grants import APIGrants
from sakura.common.tools import create_names_dict, snakecase

class APIDatabase:
    def __new__(cls, remote_api, db_info):
        db_id = db_info['database_id']
        remote_obj = remote_api.databases[db_id]
        class APIDatabaseImpl(APIObjectBase):
            __doc__ = 'Sakura Database: ' + db_info['name']
            @property
            def tables(self):
                info = self.__buffered_get_info__()
                if 'tables' not in info:
                    raise APIObjectDeniedError('access denied')
                d = create_names_dict(
                    ((table_info['name'], APITable(remote_api, table_info)) \
                     for table_info in info['tables']),
                    name_format = snakecase
                )
                return APIObjectRegistry(d, 'Sakura tables registry for this database')
            @property
            def grants(self):
                return APIGrants(remote_obj)
            def __get_remote_info__(self):
                return remote_obj.info()
        return APIDatabaseImpl()

def get_databases(remote_api):
    d = create_names_dict(
        ((remote_db_info['name'], APIDatabase(remote_api, remote_db_info)) \
         for remote_db_info in remote_api.databases.list()),
        name_format = snakecase
    )
    return APIObjectRegistry(d, 'Sakura databases registry')
