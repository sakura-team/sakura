from sakura.common.errors import APIObjectDeniedError
from sakura.client.apiobject.base import APIObjectBase, APIObjectRegistry
from sakura.client.apiobject.databases import APIDatabase
from sakura.client.apiobject.grants import APIGrants

class APIDatastore:
    def __new__(cls, remote_api, info):
        ds_id = info['datastore_id']
        remote_obj = remote_api.datastores[ds_id]
        class APIDatastoreImpl(APIObjectBase):
            __doc__ = 'Sakura %(driver_label)s datastore at %(host)s' % info
            @property
            def databases(self):
                d = { database_info['database_id']: APIDatabase(remote_api, database_info['database_id']) \
                      for database_info in self.__getattr__('databases') }
                return APIObjectRegistry(d, "Sakura databases registry for this datastore")
            @property
            def grants(self):
                return APIGrants(remote_obj)
            def __doc_attrs__(self):
                return info.items()
            def __getattr__(self, attr):
                full_info = remote_obj.info()
                if attr in full_info:
                    return full_info[attr]
                if attr == 'databases':
                    raise APIObjectDeniedError('access denied')
                raise AttributeError('No such attribute "%s"' % attr)
        return APIDatastoreImpl()

def get_datastores(remote_api):
    d = { remote_ds_info['datastore_id']: APIDatastore(remote_api, remote_ds_info) \
                for remote_ds_info in remote_api.datastores.list() }
    return APIObjectRegistry(d, 'Sakura datastores registry')
