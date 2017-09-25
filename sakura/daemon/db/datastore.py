from sakura.daemon.db import drivers
from sakura.daemon.db.database import Database

class DataStoreProber:
    def __init__(self, datastore):
        self.datastore = datastore
        self.driver = datastore.driver
    def probe(self):
        admin_conn = self.driver.connect(
            host = self.datastore.host,
            **self.datastore.admin)
        self.databases = {}
        self.driver.collect_dbs(admin_conn, self)
        self.driver.collect_db_grants(admin_conn, self)
        admin_conn.close()
        # filter-out databases with no sakura user
        databases = tuple(
                ds for ds in self.databases.values()
                if len(ds.users) > 0)
        return databases
    def register_db(self, db_name):
        self.databases[db_name] = Database(self.datastore, db_name)
    def register_grant(self, db_user, db_name, privtype):
        if db_user.startswith('sakura_'):
            user = db_user[7:]
            self.databases[db_name].grant(user, privtype)

class DataStore:
    def __init__(self, host, admin_user, admin_password, driver_label):
        self.host = host
        self.admin = dict(user = admin_user, password = admin_password)
        self.driver_label = driver_label
        self.driver = drivers.get(driver_label)
        self.databases = None    # not probed yet
        self.online = None       # not probed yet
    def refresh_databases(self):
        self.online = True
        try:
            prober = DataStoreProber(self)
            self.databases = { d.db_name: d for d in prober.probe() }
        except BaseException as exc:
            print('WARNING: %s Data Store at %s is down: %s' % \
                    (self.driver_label, self.host, str(exc).strip()))
            self.online = False
    def pack(self):
        res = dict(
            host = self.host,
            driver_label = self.driver_label,
            online = self.online
        )
        if self.online:
            databases_overview = tuple(
                database.overview() for database in self.databases.values()
            )
            res.update(
                databases = databases_overview
            )
        return res
    def __getitem__(self, database_label):
        if not self.online:
            raise AttributeError('Sorry, datastore is down.')
        return self.databases[database_label]
