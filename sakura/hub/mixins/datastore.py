from sakura.hub.tools import DaemonDataException
from sakura.hub.mixins.column import STANDARD_COLUMN_TAGS
from sakura.hub.access import ACCESS_SCOPES

DATASTORE_USER_ERROR = """\
%(driver_label)s datastore at %(host)s refers to nonexistent Sakura user "%(login)s".
This user must be created in Sakura first."""

DATASTORE_ADMIN_ERROR = """\
Daemon configuration says admin of %(driver_label)s datastore at %(host)s is nonexistent Sakura user "%(login)s".
This user must be created in Sakura first."""

class DatastoreMixin:
    @property
    def remote_instance(self):
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
        result = dict(
            daemon_id = self.daemon.id,
            datastore_id = self.id,
            online = self.online and self.daemon.connected,
            host = self.host,
            driver_label = self.driver_label,
            admin = self.admin.login,
            access_scope = ACCESS_SCOPES(self.access_scope).name
        )
        if self.online:
            result.update(
                users_rw = tuple(u.login for u in self.users_rw),
                users_ro = tuple(u.login for u in self.users_ro)
            )
        return result
    def update_online_attributes(self, context, users, **kwargs):
        # update users
        self.users_rw.clear()
        self.users_ro.clear()
        for login, createdb_grant in users:
            u = context.users.get(login = login)
            if u == None:
                raise DaemonDataException(DATASTORE_USER_ERROR % dict(
                    host = self.host,
                    driver_label = self.driver_label,
                    login = login
                ))
            if createdb_grant:
                self.users_rw.add(u)
            else:
                self.users_ro.add(u)
    @classmethod
    def create_or_update(cls, context, daemon, host, driver_label, online,
                                    admin, access_scope, **kwargs):
        access_scope = getattr(ACCESS_SCOPES, access_scope).value
        datastore = cls.get(daemon = daemon, host = host, driver_label = driver_label)
        if datastore is None:
            # new datastore attached to daemon
            datastore = cls(daemon = daemon, host = host, driver_label = driver_label,
                            online = online, access_scope = access_scope)
        else:
            datastore.online = online
            datastore.access_scope = access_scope
        admin_user = context.users.get(login = admin)
        if admin_user == None:
            raise DaemonDataException(DATASTORE_ADMIN_ERROR % dict(
                host = host,
                driver_label = driver_label,
                login = admin
            ))
        datastore.admin = admin_user
        if online:
            datastore.update_online_attributes(context, **kwargs)
        return datastore
    @classmethod
    def restore_datastore(cls, context, daemon, **ds):
        datastore = cls.create_or_update(context, daemon, **ds)
        if datastore.online:
            # if online, restore related databases
            datastore.databases = set(context.databases.restore_database(context, datastore, **db) \
                                        for db in ds['databases'])
        return datastore
