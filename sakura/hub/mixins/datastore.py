from sakura.common.access import ACCESS_SCOPES, GRANT_LEVELS
from sakura.common.errors import APIRequestErrorOfflineDatastore
from sakura.common.cache import cache_result
from sakura.hub.exceptions import DaemonDataError, \
                              DaemonDataExceptionIgnoreObject
from sakura.hub.mixins.column import STANDARD_COLUMN_TAGS
from sakura.hub.context import get_context
from sakura.hub.access import pack_gui_access_info
from sakura.hub.mixins.bases import BaseMixin

DATASTORE_USER_WARNING = """\
%(driver_label)s datastore at %(host)s refers to nonexistent Sakura user "%(login)s".
Sakura will ignore this user."""

DATASTORE_ADMIN_ERROR = """\
Daemon configuration says admin of %(driver_label)s datastore at %(host)s is nonexistent Sakura user "%(login)s".
This user must be created in Sakura first."""

class DatastoreMixin(BaseMixin):
    # Property enabled is not stored in database.
    # It should be 'volatile'.
    # Each time the hub starts, it should consider all datastores
    # are offline, until daemons tell the contrary.
    ONLINE_DATASTORES = set()

    @property
    def enabled(self):
        return self.id in DatastoreMixin.ONLINE_DATASTORES and self.daemon.enabled

    @property
    def disabled_message(self):
        if not self.daemon.enabled:
            return self.daemon.disabled_message
        if not self.id in DatastoreMixin.ONLINE_DATASTORES:
            return 'Cannot reach %s!' % self.describe()
        raise AttributeError

    @enabled.setter
    def enabled(self, value):
        changed = False
        if value and self.id not in DatastoreMixin.ONLINE_DATASTORES:
            # set online
            DatastoreMixin.ONLINE_DATASTORES.add(self.id)
            changed = True
        elif not value and self.id in DatastoreMixin.ONLINE_DATASTORES:
            # set offline
            DatastoreMixin.ONLINE_DATASTORES.remove(self.id)
            changed = True
        if changed:
            print("datastores change")
            get_context().global_events.on_datastores_change.notify()

    def on_daemon_disconnect(self):
        self.enabled = False

    def describe(self):
        return "%(driver_label)s datastore at %(host)s" % dict(
            driver_label = self.driver_label,
            host = self.host
        )

    @cache_result(2)
    def refresh(self):
        try:
            ds_info = self.raw_remote_instance.pack()
            get_context().datastores.restore_datastore(self.daemon, **ds_info)
        except BaseException as exc:
            self.enabled = False

    def assert_enabled(self):
        if not self.enabled:
            raise APIRequestErrorOfflineDatastore('Datastore is offline!')
    @property
    def raw_remote_instance(self):
        return self.daemon.api.datastores[(self.host, self.driver_label)]
    @property
    def remote_instance(self):
        self.assert_grant_level(GRANT_LEVELS.read,
                    'You are not allowed to explore this datastore.')
        self.assert_enabled()
        return self.raw_remote_instance
    def list_expected_columns_tags(self):
        # list tags already seen on this datastore
        datastore_tags = set()
        for db in self.databases:
            for tbl in db.tables:
                for col in tbl.columns:
                    datastore_tags |= set(col.user_tags)
        datastore_tags = tuple(sorted(datastore_tags))
        return STANDARD_COLUMN_TAGS + (("others", datastore_tags),)
    def pack(self):
        if self.enabled is False:
            self.refresh()   # just in case
        return dict(
            daemon_id = self.daemon.id,
            datastore_id = self.id,
            host = self.host,
            driver_label = self.driver_label,
            **self.metadata,
            **pack_gui_access_info(self),
            **self.pack_status_info()
        )
    def get_full_info(self):
        # start with general metadata
        result = self.pack()
        if self.get_grant_level() >= GRANT_LEVELS.read:
            # add info about databases
            result['databases'] = tuple(db.pack() for db in self.databases)
        return result
    def restore_grants(self, grants):
        for login, grant_level in grants.items():
            u = get_context().users.get(login = login)
            if u == None:
                # sakura user reported by daemon does not exist
                if grant_level == GRANT_LEVELS.own:
                    # this is the datastore owner written in daemon's conf!
                    raise DaemonDataError(DATASTORE_ADMIN_ERROR % dict(
                        host = self.host,
                        driver_label = self.driver_label,
                        login = login
                    ))
                else:
                    # this is another wrong sakura user found inside the
                    # datastore, just warn
                    self.daemon.api.fire_data_issue(
                        DATASTORE_USER_WARNING % dict(
                            host = self.host,
                            driver_label = self.driver_label,
                            login = login
                        ),
                        should_fail = False    # just warn
                    )
            else:
                # update
                grant = self.grants.get(login, {})
                grant.update(
                    level = grant_level
                )
                self.grants[login] = grant
    def restore_databases(self, databases):
        restored_dbs = set()
        for db in databases:
            try:
                restored_db = get_context().databases.restore_database(self, **db)
                restored_dbs.add(restored_db)
            except DaemonDataExceptionIgnoreObject as e:
                self.daemon.api.fire_data_issue(str(e), should_fail=False)
        self.databases = restored_dbs
    @classmethod
    def create_or_update(cls, daemon, host, driver_label, **kwargs):
        # create or update class
        datastore = cls.get(daemon = daemon, host = host, driver_label = driver_label)
        if datastore is None:
            # new datastore attached to daemon
            datastore = cls(daemon = daemon,
                        host = host, driver_label = driver_label)
            get_context().db.commit() # get datastore.id
        datastore.update_attributes(**kwargs)
        return datastore
    @classmethod
    def restore_datastore(cls, daemon, host, driver_label,
                            grants = None, databases = None, **ds):
        datastore = cls.create_or_update(daemon, host, driver_label, **ds)
        # if enabled, restore grants and related databases
        if datastore.enabled:
            # restore grants reported by daemon
            datastore.restore_grants(grants)
            datastore.restore_databases(databases)
        return datastore
    def update_grant(self, login, grant_name):
        self.assert_grant_level(GRANT_LEVELS.own,
                        'Only owner can change datastore grants.')
        # update on remote datastore
        self.remote_instance.update_grant(
                    login, GRANT_LEVELS.value(grant_name))
        # update in hub.db
        super().update_grant(login, grant_name)
    @classmethod
    def refresh_offline_datastores(cls):
        for ds in cls.select():
            if not ds.enabled:
                ds.refresh()
    def describe_col_tags(self):
        ds_col_tags = {}
        for db in self.databases:
            db_col_tags = db.describe_col_tags()
            if len(db_col_tags) > 0:
                ds_col_tags[db.name] = db_col_tags
        return ds_col_tags
