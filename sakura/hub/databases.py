from sakura.common.tools import SimpleAttrContainer

QUERY_ALL_DATABASES_OF_DAEMON = """
SELECT db.*, ds.online, ds.host, ds.driver as driver_label
FROM DataStore ds, Database db
WHERE db.datastore_id = ds.datastore_id
  AND ds.daemon_id = :daemon_id;
"""

QUERY_DATABASE = """
SELECT db.*, ds.online, ds.host, ds.driver as driver_label
FROM DataStore ds, Database db
WHERE db.datastore_id = ds.datastore_id
  AND db.database_id = :database_id;
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
            creation_date = self.creation_date,
            online = self.online
        )
    def get_full_info(self):
        # start with general metadata
        result = self.pack()
        # if online, explore
        if self.online:
            # ask daemon
            info_from_daemon = self.daemon.get_database_info(
                datastore_host = self.host,
                datastore_driver_label = self.driver_label,
                db_name = self.db_name
            )
            result.update(**info_from_daemon)
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
                # add columns metadata stored in db
                table_info['columns'] = tuple(
                    self.add_column_metadata(row['table_id'], info) \
                        for info in table_info['columns'])
                return table_info
    def drop_obsolete_table_metadata(self, new_db_table_names):
        old_db_table_names = set(row.db_table_name for row in \
            self.db.select('DBTable', database_id = self.database_id))
        for db_table_name in (old_db_table_names - new_db_table_names):
            self.db.delete('DBTable', database_id = self.database_id,
                                      db_table_name = db_table_name)
            self.db.commit()
    def add_column_metadata(self, table_id, column_info):
        col_name, col_type, col_tags = column_info
        db_col_tags = set(row.tag for row in \
            self.db.select('DBColumnTags', table_id=table_id, name=col_name))
        col_tags = tuple(db_col_tags | set(col_tags))   # union
        return col_name, col_type, col_tags
    def update_metadata(self, **kwargs):
        # update fields of Database table
        self.db.update('Database',
                        'database_id',
                        database_id = self.database_id,
                        **kwargs)
        # update tags
        tags = kwargs.get('tags', None)
        if tags != None:
            self.tags = tuple(tags)
            self.db.delete('DatabaseTags', database_id = self.database_id)
            for tag in tags:
                self.db.insert('DatabaseTags',
                    database_id = self.database_id, tag = tag)
        # update contacts
        contacts = kwargs.get('contacts', None)
        if contacts != None:
            self.contacts = tuple(contacts)
            self.db.delete('DatabaseContacts', database_id = self.database_id)
            for contact in contacts:
                contact_info = self.db.get_user_info(contact)
                self.db.insert('DatabaseTags',
                    database_id = self.database_id, user_id = contact_info.user_id)
        # commit
        self.db.commit()
        # update attributes of self
        self.__dict__.update(**kwargs)

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
        for info in daemon_info.datastores:
            datastore_id = datastore_ids[(info.host, info.driver_label)]
            if info.online:
                db_names = tuple(db.db_name for db in info.databases)
                self.restore_databases_for_datastore(datastore_id, db_names)
        # retrieve updated info from db (because we need the ids)
        db_rows = self.db.execute(QUERY_ALL_DATABASES_OF_DAEMON, daemon_id = daemon_id)
        self.reload_databases_from_db(daemon_info.api, db_rows)
    def reload_databases_from_db(self, daemon, db_rows):
        for row in db_rows:
            database_id = row.database_id
            tags = tuple(row.tag for row in \
                        self.db.select('DatabaseTags', database_id = database_id))
            contacts = tuple(row.login for row in \
                        self.db.execute(QUERY_DB_CONTACTS, database_id = database_id))
            self.info_per_database_id[database_id] = DatabaseInfo(
                daemon = daemon,
                db = self.db,
                tags = tags,
                contacts = contacts,
                **row)
    def reload_database_from_db(self, daemon, database_id):
        db_rows = self.db.execute(QUERY_DATABASE, database_id = database_id)
        self.reload_databases_from_db(daemon, db_rows)  # actually, len(db_rows) == 1
    def restore_databases_for_datastore(self, datastore_id, db_names):
        new_db_names = set(db_names)
        old_db_names = set(row.db_name for row in \
                self.db.select('Database', datastore_id = datastore_id))
        # forget obsolete databases from db
        for db_name in old_db_names - new_db_names:
            self.db.delete('Database', db_name=db_name, datastore_id=datastore_id)
        # add new databases in db
        for db_name in new_db_names - old_db_names:
            self.db.insert('Database', datastore_id=datastore_id, db_name=db_name, name=db_name)
        # if any change was made, commit
        if len(old_db_names ^ new_db_names) > 0:
            self.db.commit()
