import re
from sakura.common.tools import SimpleAttrContainer, greenlet_env

class DataStoreInfo(SimpleAttrContainer):
    def pack(self):
        result = dict(
            daemon_id = self.daemon_id,
            datastore_id = self.datastore_id,
            online = self.online,
            host = self.host,
            driver_label = self.driver_label,
            admin = self.admin
        )
        if self.online:
            result.update(
                users_rw = self.users_rw,
                users_ro = self.users_ro
            )
        return result
    def generate_db_name(self, name):
        # compute a name containing only lowercase letters, numbers
        # or underscore, and not used already
        base_db_name = 'sakura_' + re.sub('[^a-z0-9]+', '_', name)
        suffix_index = 0
        db_name = base_db_name
        while True:
            row = self.db.select_unique('Database',
                datastore_id = self.datastore_id, db_name = db_name)
            if row is None:
                return db_name  # OK db_name is free
            else:
                db_name = base_db_name + '_' + str(suffix_index)
    def create_db(self, name):
        db_name = self.generate_db_name(name)
        # insert in central db
        self.db.insert('Database', name = name, db_name = db_name, \
                        datastore_id = self.datastore_id)
        # request daemon to create db on the remote datastore
        self.daemon.create_db(self.host, self.driver_label, db_name, \
                                greenlet_env.user)
        # return database_id
        row = self.db.select_unique('Database', db_name = db_name, \
                        datastore_id = self.datastore_id)
        return row.database_id

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
            datastore_ids[(host, driver_label)] = datastore_id
            datastore_info = dict(
                    daemon_id = daemon_id,
                    datastore_id = datastore_id,
                    online = online,
                    host = host,
                    driver_label = driver_label,
                    admin = admin_username,
                    db = self.db,
                    daemon = daemon_info.api
            )
            if online:
                users = new_datastore_dict[(host, driver_label)].users
                users_rw = tuple(user for user, createdb_grant in users if createdb_grant)
                users_ro = tuple(user for user, createdb_grant in users if not createdb_grant)
                datastore_info.update(users_rw = users_rw, users_ro = users_ro)
            self.info_per_datastore_id[datastore_id] = DataStoreInfo(**datastore_info)
        return datastore_ids
