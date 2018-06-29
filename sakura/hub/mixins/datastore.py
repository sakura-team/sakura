from sakura.common.access import ACCESS_SCOPES, GRANT_LEVELS
from sakura.common.errors import APIRequestErrorOfflineDatastore
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
    # Property online is not stored in database.
    # It should be 'volatile'.
    # Each time the hub starts, it should consider all datastores
    # are offline, until daemons tell the contrary.
    ONLINE_DATASTORES = set()

    @property
    def online(self):
        return self.id in DatastoreMixin.ONLINE_DATASTORES

    @online.setter
    def online(self, value):
        if value:   # set online
            DatastoreMixin.ONLINE_DATASTORES.add(self.id)
        else:       # set offline
            if self.id in DatastoreMixin.ONLINE_DATASTORES:
                DatastoreMixin.ONLINE_DATASTORES.remove(self.id)

    def describe(self):
        return "%(driver_label)s datastore at %(host)s" % dict(
            driver_label = self.driver_label,
            host = self.host
        )
    def assert_online(self):
        if not self.online:
            raise APIRequestErrorOfflineDatastore('Datastore is offline!')
    @property
    def remote_instance(self):
        self.assert_grant_level(GRANT_LEVELS.read,
                    'You are not allowed to explore this datastore.')
        self.assert_online()
        return self.daemon.api.datastores[(self.host, self.driver_label)]
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
        return dict(
            daemon_id = self.daemon.id,
            datastore_id = self.id,
            online = self.online and self.daemon.connected,
            host = self.host,
            driver_label = self.driver_label,
            **self.metadata,
            **pack_gui_access_info(self)
        )
    def restore_grants(self, grants):
        cleaned_up_grants = {}
        for login, grant in grants.items():
            u = get_context().users.get(login = login)
            if u == None:
                # sakura user reported by daemon does not exist
                if grant == GRANT_LEVELS.own:
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
                cleaned_up_grants[login] = grant
        self.grants = cleaned_up_grants
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
        # if online, restore grants and related databases
        if datastore.online:
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
