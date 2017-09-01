from sakura.common.tools import SimpleAttrContainer

class DataStoreRegistry(object):
    def __init__(self, db):
        self.db = db
        self.info_per_datastore_id = {}
    def list(self):
        return tuple(self.info_per_datastore_id.values())
    def __getitem__(self, datastore_id):
        return self.info_per_datastore_id[datastore_id]
    def restore_daemon_state(self, daemon_info):
        daemon_id = daemon_info.daemon_id
        new_datastore_dict = {
            (info.host, info.driver_label): info \
            for info in daemon_info.datastores }
        new_datastore_keys = set(new_datastore_dict)
        old_datastore_dict = {
            (row['host'], row['driver']) : row \
            for row in self.db.select('DataStore', daemon_id=daemon_id)}
        old_datastore_keys = set(old_datastore_dict)
        # forget obsolete data stores and corresponding datasets from db
        for datastore_key in old_datastore_keys - new_datastore_keys:
            datastore_id = old_datastore_dict[datastore_key]['datastore_id']
            # note this will also delete related datasets
            # (because of ON DELETE CASCADE clause on db schema)
            self.db.delete('DataStore', datastore_id=datastore_id)
        # add new data stores in db
        for key in new_datastore_keys - old_datastore_keys:
            self.db.insert('DataStore', daemon_id=daemon_id, host=key[0], driver=key[1])
        # if any change was made, commit
        if len(new_datastore_keys ^ old_datastore_keys) > 0:
            self.db.commit()
        # retrieve updated info from db (because we need the ids)
        # and prepare info that will be needed for datasets registry
        datasets_info = []
        for row in self.db.select('DataStore', daemon_id=daemon_id):
            datastore_id, host, driver_label = \
                row['datastore_id'], row['host'], row['driver']
            info = new_datastore_dict[(host, driver_label)]
            datasets_info.append((datastore_id, info.datasets))
            self.info_per_datastore_id[datastore_id] = \
                SimpleAttrContainer(
                    daemon_id = daemon_id,
                    datastore_id = datastore_id,
                    host = host,
                    driver_label = driver_label
                )
        return datasets_info
