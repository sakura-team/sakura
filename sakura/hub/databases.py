from sakura.common.tools import SimpleAttrContainer

QUERY_ONLINE_DATABASES_OF_DAEMON = """
SELECT Database.*
FROM DataStore, Database
WHERE DataStore.datastore_id = Database.datastore_id
  AND DataStore.daemon_id = :daemon_id
  AND DataStore.online = 1;
"""

QUERY_ALL_DATABASES_OF_DAEMON = """
SELECT Database.*, DataStore.online
FROM DataStore, Database
WHERE DataStore.datastore_id = Database.datastore_id
  AND DataStore.daemon_id = :daemon_id;
"""

QUERY_DB_CONTACTS = """
SELECT User.*
FROM User, DatabaseContacts
WHERE User.user_id = DatabaseContacts.user_id
  AND DatabaseContacts.database_id = :database_id
"""

class DatabaseRegistry(object):
    def __init__(self, db):
        self.db = db
        self.info_per_database_id = {}
    def list(self):
        return tuple(self.info_per_database_id.values())
    def __getitem__(self, database_id):
        return self.info_per_database_id[database_id]
    def restore_daemon_state(self, daemon_info, datastore_ids):
        daemon_id = daemon_info.daemon_id
        new_online_database_dict = {}
        for info in daemon_info.datastores:
            datastore_id = datastore_ids[(info.host, info.driver_label)]
            if info.online:
                for database in info.databases:
                    key = (datastore_id, database.db_name)
                    new_online_database_dict[key] = database
        new_online_database_keys = set(new_online_database_dict)
        old_online_database_dict = {
            (row.datastore_id, row.db_name) : row \
            for row in self.db.execute(QUERY_ONLINE_DATABASES_OF_DAEMON, daemon_id = daemon_id)}
        old_online_database_keys = set(old_online_database_dict)
        # forget obsolete databases from db
        for database_key in old_online_database_keys - new_online_database_keys:
            database_id = old_online_database_dict[database_key].database_id
            self.db.delete('Database', database_id=database_id)
        # add new databases in db
        for key in new_online_database_keys - old_online_database_keys:
            self.db.insert('Database', datastore_id=key[0], db_name=key[1], name=key[1])
        # if any change was made, commit
        if len(new_online_database_keys ^ old_online_database_keys) > 0:
            self.db.commit()
        # retrieve updated info from db (because we need the ids)
        for row in self.db.execute(QUERY_ALL_DATABASES_OF_DAEMON, daemon_id = daemon_id):
            database_id = row.database_id
            tags = tuple(row.tag for row in \
                        self.db.select('DatabaseTags', database_id = database_id))
            contacts = tuple(dict(**row) for row in \
                        self.db.execute(QUERY_DB_CONTACTS, database_id = database_id))
            self.info_per_database_id[database_id] = SimpleAttrContainer(
                tags = tags,
                contacts = contacts,
                **row)
