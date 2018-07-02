import time
from enum import Enum
from sakura.common.access import ACCESS_SCOPES, GRANT_LEVELS
from sakura.hub.exceptions import DaemonDataExceptionIgnoreObject
from sakura.hub.context import get_context
from sakura.hub.access import pack_gui_access_info, parse_gui_access_info, \
                              find_owner
from sakura.hub.mixins.bases import BaseMixin

class DatabaseMixin(BaseMixin):
    @property
    def online(self):
        return self.datastore.online and self.datastore.daemon.connected
    @property
    def remote_instance(self):
        self.datastore.assert_online()
        self.assert_grant_level(GRANT_LEVELS.read,
                    'You are not allowed to read data from this database.')
        ds_key = (self.datastore.host, self.datastore.driver_label)
        remote_ds = self.datastore.daemon.api.datastores[ds_key]
        return remote_ds.databases[self.name]
    def pack(self):
        result = dict(
            database_id = self.id,
            datastore_id = self.datastore.id,
            name = self.name,
            online = self.online,
            **self.metadata,
            **pack_gui_access_info(self)
        )
        result.update(**self.metadata)
        return result
    def describe(self):
        return "%(name)s database (on %(ds)s)" % dict(
            name = self.name,
            ds = self.datastore.describe()
        )
    def get_full_info(self):
        # start with general metadata
        result = self.pack()
        # if online and sufficient grant, explore tables
        if self.online and self.get_grant_level() >= GRANT_LEVELS.read:
            self.update_tables_from_daemon()
            result['tables'] = tuple(t.pack() for t in self.tables)
        return result
    def update_tables_from_daemon(self):
        context = get_context()
        # ask daemon
        info_from_daemon = self.remote_instance.pack()
        # update tables (except foreign keys - a referenced table
        # may not be created yet otherwise)
        tables = set()
        for tbl_info in info_from_daemon['tables']:
            info = dict(tbl_info)
            del info['foreign_keys']
            tables.add(context.tables.restore_table(self, **info)
        )
        self.tables = tables
        context.db.commit() # make sure db id's are set
        # update foreign keys
        for tbl_info in info_from_daemon['tables']:
            table = context.tables.get(
                database = self,
                name = tbl_info['name']
            )
            table.update_foreign_keys(tbl_info['foreign_keys'])
    def create_on_datastore(self):
        self.datastore.remote_instance.create_db(
                self.name,
                self.owner)
    @classmethod
    def create_or_update(cls, datastore, name, **kwargs):
        database = cls.get(datastore = datastore, name = name)
        if database is None:
            # new database detected on a daemon
            grants = kwargs.pop('grants', {})
            database = cls( datastore = datastore,
                            name = name,
                            grants = grants)
        database.update_attributes(**kwargs)
        database.cleanup_grants()
        # if owner not specified by daemon, set it to datastore's admin
        if database.owner is None:
            database.owner = datastore.owner
        return database
    def refresh_metadata_from_daemon(self):
        daemon_info = self.remote_instance.overview()
        get_context().databases.restore_database(self.datastore, **daemon_info)
    @classmethod
    def restore_database(cls, datastore, **db):
        return cls.create_or_update(datastore, **db)
    @classmethod
    def create_db(cls, datastore, name, creation_date = None, **kwargs):
        datastore.assert_grant_level(GRANT_LEVELS.write,
                    'You are not allowed to create a database on this datastore.')
        context = get_context()
        current_user = context.session.user
        if creation_date is None:
            creation_date = time.time()
        # parse access info from gui
        kwargs = parse_gui_access_info(**kwargs)
        # owner is current user
        grants = kwargs.pop('grants', {})
        grants[current_user.login] = GRANT_LEVELS.own
        # register in central db
        new_db = cls.create_or_update(
                        datastore = datastore,
                        name = name,
                        grants = grants,
                        creation_date = creation_date,
                        **kwargs)
        # request daemon to create db on the remote datastore
        new_db.create_on_datastore()
        # return database_id
        context.db.commit()
        return new_db.id
    def update_grant(self, login, grant_name):
        self.assert_grant_level(GRANT_LEVELS.own,
                        'Only owner can change database grants.')
        self.datastore.remote_instance.update_database_grant(
                    self.name, login, GRANT_LEVELS.value(grant_name))
        self.refresh_metadata_from_daemon()
