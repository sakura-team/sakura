from sakura.common.tools import SimpleAttrContainer

QUERY_DATASETS_FROM_DAEMON = """
SELECT Database.*
FROM DataStore, Database
WHERE DataStore.datastore_id = Database.datastore_id
  AND DataStore.daemon_id = %d;
"""

class DatabaseRegistry(object):
    def __init__(self, db):
        self.db = db
        self.info_per_database_id = {}
    def list(self):
        return tuple(self.info_per_database_id.values())
    def __getitem__(self, database_id):
        return self.info_per_database_id[database_id]
    def restore_daemon_state(self, daemon_id, databases_info):
        new_database_dict = {}
        for datastore_id, databases in databases_info:
            for database in databases:
                key = (datastore_id, database.label)
                new_database_dict[key] = database
        new_database_keys = set(new_database_dict)
        old_database_dict = {
            (row['datastore_id'], row['label']) : row \
            for row in self.db.execute(QUERY_DATASETS_FROM_DAEMON % daemon_id)}
        old_database_keys = set(old_database_dict)
        # forget obsolete databases from db
        for database_key in old_database_keys - new_database_keys:
            database_id = old_database_dict[database_key]['database_id']
            self.db.delete('Database', database_id=database_id)
        # add new databases in db
        for key in new_database_keys - old_database_keys:
            self.db.insert('Database', datastore_id=key[0], label=key[1])
        # if any change was made, commit
        if len(new_database_keys ^ old_database_keys) > 0:
            self.db.commit()
        # retrieve updated info from db (because we need the ids)
        for row in self.db.execute(QUERY_DATASETS_FROM_DAEMON % daemon_id):
            database_id, datastore_id, label = \
                row['database_id'], row['datastore_id'], row['label']
            self.info_per_database_id[database_id] = SimpleAttrContainer(
                datastore_id = datastore_id,
                database_id = database_id,
                label = label
            )
