from sakura.daemon.db import drivers
from sakura.daemon.db import adapters
from sakura.daemon.db.database import Database

class DataStoreProber:
    def __init__(self, datastore):
        self.datastore = datastore
        self.driver = datastore.driver
    def probe(self):
        print("DS probing start: %s" % self.datastore.host)
        admin_conn = self.datastore.admin_connect()
        self.users = []
        self.databases = {}
        self.driver.collect_users(admin_conn, self)
        self.driver.collect_dbs(admin_conn, self)
        self.driver.collect_db_grants(admin_conn, self)
        admin_conn.close()
        # filter-out databases with no sakura user
        databases = tuple(
                ds for ds in self.databases.values()
                if len(ds.users) > 0)
        return self.users, databases
    def register_user(self, db_user, createdb_grant):
        user = self.as_sakura_user(db_user)
        if user:
            self.users.append((user, createdb_grant))
    def register_db(self, db_name):
        print("DS probing: found database %s" % db_name)
        self.databases[db_name] = Database(self.datastore, db_name)
    def as_sakura_user(self, db_user):
        if db_user.startswith('sakura_'):
            return db_user[7:]
    def register_grant(self, db_user, db_name, privtype):
        user = self.as_sakura_user(db_user)
        if user:
            self.databases[db_name].grant(user, privtype)

class DataStore:
    def __init__(self, host, datastore_admin, sakura_admin,
                 driver_label, adapter_label):
        self.host = host
        self.datastore_admin = datastore_admin
        self.sakura_admin = sakura_admin
        self.driver_label = driver_label
        self.driver = drivers.get(driver_label)
        self._users = None        # not probed yet
        self._databases = None    # not probed yet
        self._online = None       # not probed yet
        self.adapter = adapters.get(adapter_label)
    def admin_connect(self):
        return self.driver.connect(
            host = self.host,
            **self.datastore_admin)
    @property
    def users(self):
        if self._users is None:
            self.refresh()
        return self._users
    @property
    def databases(self):
        if self._databases is None:
            self.refresh()
        return self._databases
    @property
    def online(self):
        if self._online is None:
            self.refresh()
        return self._online
    def refresh(self):
        try:
            prober = DataStoreProber(self)
            self._users, databases = prober.probe()
            self._databases = { d.db_name: d for d in databases }
            self._online = True
        except BaseException as exc:
            print('WARNING: %s Data Store at %s is down: %s' % \
                    (self.driver_label, self.host, str(exc).strip()))
            self._online = False
    def pack(self):
        res = dict(
            host = self.host,
            driver_label = self.driver_label,
            admin = self.sakura_admin,
            online = self.online
        )
        if self.online:
            databases_overview = tuple(
                database.overview() for database in self.databases.values()
            )
            res.update(
                users = self.users,
                databases = databases_overview
            )
        return res
    def __getitem__(self, database_label):
        if not self.online:
            raise AttributeError('Sorry, datastore is down.')
        return self.databases[database_label]
    def create_db(self, db_name, owner):
        admin_conn = self.admin_connect()
        self.driver.create_db(admin_conn, db_name, 'sakura_' + owner)
        admin_conn.close()
        self.refresh()
