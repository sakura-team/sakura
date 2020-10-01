import time
from enum import Enum
from sakura.common.access import ACCESS_SCOPES, GRANT_LEVELS
from sakura.common.cache import cache_result
from sakura.hub.exceptions import DaemonDataExceptionIgnoreObject
from sakura.hub.context import get_context
from sakura.hub.access import pack_gui_access_info, parse_gui_access_info, \
                              find_owner, parse_daemon_grants
from sakura.hub.mixins.bases import BaseMixin

class DatabaseMixin(BaseMixin):
    @property
    def enabled(self):
        return self.datastore.enabled
    @property
    def disabled_message(self):
        return self.datastore.disabled_message
    @property
    def readable(self):
        return self.enabled and self.get_grant_level() >= GRANT_LEVELS.read
    @property
    def remote_instance(self):
        self.datastore.assert_enabled()
        self.assert_grant_level(GRANT_LEVELS.read,
                    'You are not allowed to read data from this database.')
        ds_key = (self.datastore.host, self.datastore.driver_label)
        remote_ds = self.datastore.daemon.api.datastores[ds_key]
        return remote_ds.databases[self.name]
    def pack(self):
        return dict(
            database_id = self.id,
            datastore_id = self.datastore.id,
            name = self.name,
            **self.metadata,
            **pack_gui_access_info(self),
            **self.pack_status_info()
        )
    def describe(self):
        return "%(name)s database (on %(ds)s)" % dict(
            name = self.name,
            ds = self.datastore.describe()
        )
    def get_full_info(self):
        # start with general metadata
        result = self.pack()
        # if enabled and sufficient grant, explore tables
        if self.readable:
            self.update_tables_from_daemon()
            result['tables'] = tuple(t.pack() for t in self.tables)
        return result
    @cache_result(5)    # do not call this too often
    def update_tables_from_daemon(self):
        if not self.readable:
            raise APIObjectDeniedError('You are not allowed to read this database.')
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
    def create_or_update(cls, datastore, name, grants={}, **kwargs):
        database = cls.get(datastore = datastore, name = name)
        if database is None:
            # new database detected on a daemon
            database = cls( datastore = datastore,
                            name = name,
                            grants = grants)
        database.update_attributes(**kwargs)
        # if owner not specified by daemon, set it to datastore's admin
        if database.owner is None:
            database.owner = datastore.owner
        return database
    def refresh_metadata_from_daemon(self):
        daemon_info = self.remote_instance.overview()
        get_context().databases.restore_database(self.datastore, **daemon_info)
    @classmethod
    def restore_database(cls, datastore, grants, **kwargs):
        grants = parse_daemon_grants(grants)
        return cls.create_or_update(datastore, grants = grants, **kwargs)
    @classmethod
    def create_db(cls, datastore, name, creation_date = None, **kwargs):
        datastore.assert_grant_level(GRANT_LEVELS.write,
                    'You are not allowed to create a database on this datastore.')
        context = get_context()
        if creation_date is None:
            creation_date = time.time()
        # parse access info from gui
        kwargs = parse_gui_access_info(**kwargs)
        # owner is current user
        grants = { context.user.login: { 'level': GRANT_LEVELS.own }}
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
        # update hub db
        super().update_grant(login, grant_name)
        # update remotely on datastore
        self.datastore.remote_instance.update_database_grant(
                    self.name, login, GRANT_LEVELS.value(grant_name))
    def delete_database(self):
        self.assert_grant_level(GRANT_LEVELS.own,
                'Only owner is allowed to delete this database.')
        # delete table on datastore
        self.datastore.remote_instance.delete_database(self.name)
        # delete instance in local db
        self.delete()
    def describe_col_tags(self):
        db_col_tags = {}
        for tbl in self.tables:
            tbl_col_tags = tbl.describe_col_tags()
            if len(tbl_col_tags) > 0 and max(map(len, tbl_col_tags)) > 0:
                db_col_tags[tbl.name] = tbl_col_tags
        return db_col_tags
