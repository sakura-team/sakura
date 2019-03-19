from sakura.common.access import ACCESS_SCOPES
from sakura.daemon.db.datastore import DataStore
import sakura.daemon.conf as conf

def load_datastores(engine):
    datastores = []
    for ds_conf in conf.data_stores:
        ds = DataStore(
            engine = engine,
            host = ds_conf.host,
            datastore_admin = ds_conf.datastore_admin,
            sakura_admin = ds_conf.sakura_admin,
            driver_label = ds_conf.driver,
            adapter_label = ds_conf.get('adapter', 'native'),
            access_scope = ACCESS_SCOPES.value(
                    ds_conf.get('access_scope', 'private'))
        )
        ds.refresh()
        datastores.append(ds)
    return datastores
