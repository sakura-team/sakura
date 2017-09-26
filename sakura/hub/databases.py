from sakura.common.tools import SimpleAttrContainer

QUERY_ONLINE_DATABASES_OF_DAEMON = """
SELECT Database.*
FROM DataStore, Database
WHERE DataStore.datastore_id = Database.datastore_id
  AND DataStore.daemon_id = :daemon_id
  AND DataStore.online = 1;
"""

QUERY_ALL_DATABASES_OF_DAEMON = """
SELECT db.*, ds.online, ds.host, ds.driver as driver_label
FROM DataStore ds, Database db
WHERE ds.datastore_id = ds.datastore_id
  AND ds.daemon_id = :daemon_id;
"""

QUERY_DB_CONTACTS = """
SELECT User.*
FROM User, DatabaseContacts
WHERE User.user_id = DatabaseContacts.user_id
  AND DatabaseContacts.database_id = :database_id
"""

class DatabaseInfo(SimpleAttrContainer):
    def pack(self):
        return dict(
            tags = self.tags,
            contacts = self.contacts,
            database_id = self.database_id,
            datastore_id = self.datastore_id,
            name = self.name,
            short_desc = self.short_desc,
            created = self.created
        )
    def get_full_info(self):
        if not self.online:
            print('Sorry, this database is offline!')
            return None
        # ask daemon
        result = self.daemon.api.get_database_info(
            datastore_host = self.host,
            datastore_driver_label = self.driver_label,
            db_name = self.db_name
        )
        # add general metadata
        result.update(**self.pack())
        # add tables metadata stored in db
        result['tables'] = tuple(
            self.add_table_metadata(info) for info in result['tables'])
        # drop obsolete table metadata from db
        db_table_names = set(table['db_table_name'] for table in result['tables'])
        self.drop_obsolete_table_metadata(db_table_names)
        return result
    def add_table_metadata(self, table_info):
        db_table_name = table_info['db_table_name']
        while True:
            row = self.db.select_unique('DBTable',
                    database_id = self.database_id,
                    db_table_name = db_table_name)
            if row is None:
                self.db.insert('DBTable',
                        database_id = self.database_id,
                        name = db_table_name,
                        db_table_name = db_table_name)
                self.db.commit()
            else:
                table_info.update(**row)
                return table_info
    def drop_obsolete_table_metadata(self, new_db_table_names):
        old_db_table_names = set(row.db_table_name for row in \
            self.db.select('DBTable', database_id = self.database_id))
        for db_table_name in (old_db_table_names - new_db_table_names):
            self.db.delete('DBTable', database_id = self.database_id,
                                      db_table_name = db_table_name)
            self.db.commit()

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
            self.info_per_database_id[database_id] = DatabaseInfo(
                daemon = daemon_info,
                db = self.db,
                tags = tags,
                contacts = contacts,
                **row)
