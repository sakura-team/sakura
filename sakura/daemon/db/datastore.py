from sakura.daemon.db import drivers
from sakura.daemon.db import adapters
from sakura.daemon.db.grants import register_grant
from sakura.daemon.db.database import Database
from sakura.daemon.db.pool import ConnectionPool
from sakura.common.io import pack
from sakura.common.access import GRANT_LEVELS
from sakura.common.password import decode_password
from sakura.common.cache import cache_result
from sakura.common.errors import APIRequestErrorOfflineDatastore

class DataStoreProber:
    def __init__(self, datastore):
        self.datastore = datastore
        self.driver = datastore.driver
    def probe(self):
        print("DS probing start: %s" % self.datastore.host)
        admin_conn = self.datastore.admin_connect()
        self.grants = { self.datastore.sakura_admin: GRANT_LEVELS.own }
        self.databases = {}
        self.driver.collect_grants(admin_conn, self)
        self.driver.collect_databases(admin_conn, self)
        self.driver.collect_database_grants(admin_conn, self)
        admin_conn.close()
        return self.grants, self.databases.values()
    def register_datastore_grant(self, db_user, grant):
        register_grant(self.grants, db_user, grant)
    def register_database(self, db_name):
        print("DS probing: found database %s" % db_name)
        self.databases[db_name] = Database(self.datastore, db_name)
    def register_database_grant(self, db_user, db_name, grant):
        self.databases[db_name].register_grant(db_user, grant)

class DataStore:
    def __init__(self, engine, host, datastore_admin, sakura_admin,
                 driver_label, adapter_label, access_scope):
        self.engine = engine
        self.host = host
        self.datastore_admin = datastore_admin
        self.sakura_admin = sakura_admin
        self.driver_label = driver_label
        self.driver = drivers.get(driver_label)
        self._grants = None        # not probed yet
        self._databases = None    # not probed yet
        self._online = None       # not probed yet
        self.adapter = adapters.get(adapter_label)
        self.access_scope = access_scope
        self.conn_pools = {}
    def unique_id(self):
        return ('Datastore', self.host, self.driver_label)
    def admin_connect(self, db_name = None):
        pool = self.conn_pools.get(db_name)
        if pool is None:
            pool = ConnectionPool(lambda: self.do_admin_connect(db_name))
            self.conn_pools[db_name] = pool
        return pool.connect()
    def do_admin_connect(self, db_name):
        info = dict(
            host = self.host,
            **self.datastore_admin
        )
        encoded_password = info.pop('encoded_password', None)
        if encoded_password is not None:
            info.update(
                password = decode_password(encoded_password)
            )
        if db_name is not None:
            info.update(dbname = db_name)
        try:
            return self.driver.connect(**info)
        except BaseException as e:
            print(str(e))
            self._online = False
            exc = APIRequestErrorOfflineDatastore('Datastore is down!')
            exc.data = dict(host = self.host, driver_label = self.driver_label)
            raise exc
    @property
    def grants(self):
        if self._grants is None:
            self.refresh()
        return self._grants
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
    @cache_result(2)
    def refresh(self):
        try:
            prober = DataStoreProber(self)
            self._grants, databases = prober.probe()
            self._databases = { d.db_name: d for d in databases }
            self._online = True
        except BaseException as exc:
            print('WARNING: %s Data Store at %s is down: %s' % \
                    (self.driver_label, self.host, str(exc).strip()))
            self._online = False
    def pack(self):
        if self._online is False:
            self.refresh()
        res = dict(
            host = self.host,
            driver_label = self.driver_label,
            enabled = self.online,
            access_scope = self.access_scope,
            admin = self.sakura_admin
        )
        if self.online:
            databases_overview = tuple(
                database.overview() for database in self.databases.values()
            )
            res.update(
                grants = self.grants,
                databases = databases_overview
            )
        return pack(res)
    def __getitem__(self, database_label):
        if not self.online:
            raise AttributeError('Sorry, datastore is down.')
        return self.databases[database_label]
    def create_db(self, db_name, owner):
        db_owner = 'sakura_' + owner
        with self.admin_connect() as admin_conn:
            if not self.driver.has_user(admin_conn, db_owner):
                self.driver.create_user(admin_conn, db_owner)
            self.driver.create_db(admin_conn, db_name, db_owner)
        self.refresh()
    def update_database_grant(self, db_name, login, grant_level):
        db_user = 'sakura_' + login
        with self.admin_connect() as admin_conn:
            if not self.driver.has_user(admin_conn, db_user):
                self.driver.create_user(admin_conn, db_user)
            self.driver.set_database_grant(
                    admin_conn, db_name, db_user, grant_level)
        self.refresh()
    def update_grant(self, login, grant_level):
        ds_user = 'sakura_' + login
        with self.admin_connect() as admin_conn:
            if not self.driver.has_user(admin_conn, ds_user):
                self.driver.create_user(admin_conn, ds_user)
            self.driver.set_datastore_grant(
                    admin_conn, ds_user, grant_level)
        self.refresh()
    def delete_database(self, db_name):
        with self.admin_connect() as admin_conn:
            self.driver.delete_db(admin_conn, db_name)
        self.refresh()
    @property
    def col_tags_info(self):
        if (self.host, self.driver_label) not in self.engine.col_tags_info:
            self.engine.col_tags_info[(self.host, self.driver_label)] = {}
        return self.engine.col_tags_info[(self.host, self.driver_label)]
