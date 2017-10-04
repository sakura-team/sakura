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
        db_updated = False
        daemon_id = daemon_info.daemon_id
        new_datastore_dict = {
            (info.host, info.driver_label): info \
            for info in daemon_info.datastores }
        new_datastore_keys = set(new_datastore_dict)
        old_datastore_dict = {
            (row.host, row.driver) : row \
            for row in self.db.select('DataStore', daemon_id=daemon_id)}
        old_datastore_keys = set(old_datastore_dict)
        # forget obsolete data stores and corresponding databases from db
        for datastore_key in old_datastore_keys - new_datastore_keys:
            datastore_id = old_datastore_dict[datastore_key].datastore_id
            # note this will also delete related databases
            # (because of ON DELETE CASCADE clause on db schema)
            self.db.delete('DataStore', datastore_id=datastore_id)
            db_updated = True
        # add new data stores in db
        for key in new_datastore_keys - old_datastore_keys:
            self.db.insert('DataStore',
                daemon_id=daemon_id, host=key[0], driver=key[1],
                online=new_datastore_dict[key].online)
            db_updated = True
        # update online flag if needed
        for key in new_datastore_keys & old_datastore_keys:
            if new_datastore_dict[key].online != old_datastore_dict[key].online:
                self.db.update('DataStore', 'datastore_id',
                    datastore_id = old_datastore_dict[key].datastore_id,
                    online = new_datastore_dict[key].online
                )
                db_updated = True
        # if any change was made, commit
        if db_updated:
            self.db.commit()
        # retrieve updated info from db (because we need the ids)
        datastore_ids = {}
        for row in self.db.select('DataStore', daemon_id=daemon_id):
            datastore_id, online, host, driver_label = \
                row.datastore_id, row.online, row.host, row.driver
            admin_username = new_datastore_dict[(host, driver_label)].admin
            admin_info = self.db.get_user_info(admin_username)
            datastore_ids[(host, driver_label)] = datastore_id
            datastore_info = dict(
                    daemon_id = daemon_id,
                    datastore_id = datastore_id,
                    online = online,
                    host = host,
                    driver_label = driver_label,
                    admin = admin_info
            )
            if online:
                users = new_datastore_dict[(host, driver_label)].users
                users_info = tuple( (self.db.get_user_info(user), createdb_grant) \
                                    for user, createdb_grant in users)
                datastore_info.update(users = users_info)
            self.info_per_datastore_id[datastore_id] = \
                        SimpleAttrContainer(**datastore_info)
        return datastore_ids
