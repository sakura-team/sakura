from sakura.common.errors import APIObjectDeniedError
from sakura.client.apiobject.base import APIObjectBase, APIObjectRegistry
from sakura.client.apiobject.databases import APIDatabase
from sakura.client.apiobject.grants import APIGrants
from sakura.common.tools import create_names_dict, snakecase

class APIDatastore:
    def __new__(cls, remote_api, info):
        ds_id = info['datastore_id']
        remote_obj = remote_api.datastores[ds_id]
        class APIDatastoreImpl(APIObjectBase):
            __doc__ = 'Sakura %(driver_label)s datastore at %(host)s' % info
            @property
            def databases(self):
                info = self.__buffered_get_info__()
                if 'databases' not in info:
                    raise APIObjectDeniedError('access denied')
                d = create_names_dict(
                    ((database_info['name'], APIDatabase(remote_api, database_info)) \
                     for database_info in info['databases']),
                    name_format = snakecase
                )
                return APIObjectRegistry(d, "Sakura databases registry for this datastore")
            @property
            def grants(self):
                return APIGrants(remote_obj)
            def __get_remote_info__(self):
                return remote_obj.info()
        return APIDatastoreImpl()

def get_datastores(remote_api):
    d = create_names_dict(
        ((ds_info['driver_label'] + '_' + ds_info['host'], APIDatastore(remote_api, ds_info)) \
         for ds_info in remote_api.datastores.list()),
        name_format = snakecase
    )
    return APIObjectRegistry(d, 'Sakura datastores registry')
