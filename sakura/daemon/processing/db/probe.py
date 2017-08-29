from sakura.daemon.processing.db.table import DBTable
from sakura.daemon.processing.db.dataset import Dataset

class DataStoreProber:
    def __init__(self, data_store):
        self.data_store = data_store
        self.driver = data_store.driver
    def probe(self):
        admin_conn = self.driver.connect(
            host = self.data_store.host,
            **self.data_store.admin)
        self.datasets = {}
        self.driver.collect_dbs(admin_conn, self)
        self.driver.collect_db_grants(admin_conn, self)
        admin_conn.close()
        # filter-out databases with no sakura user
        datasets = tuple(
                ds for ds in self.datasets.values()
                if len(ds.users) > 0)
        return datasets
    def register_db(self, db_name):
        self.datasets[db_name] = Dataset(self.data_store, db_name)
    def register_grant(self, db_user, db_name, privtype):
        if db_user.startswith('sakura_'):
            user = db_user[7:]
            self.datasets[db_name].grant(user, privtype)

class DBProber:
    def __init__(self, db_driver, db_conn):
        self.driver = db_driver
        self.db_name = None     # not probed yet
        self.db_conn = db_conn
    def probe(self):
        self.tables = {}
        self.db_name = self.driver.get_current_db_name(self.db_conn)
        self.driver.collect_db_tables(self.db_conn, self)
        return self.tables
    def register_table(self, table_name):
        print("DB probing: found table %s" % table_name)
        self.tables[table_name] = DBTable(self.db_name, table_name)
        self.driver.collect_table_columns(self.db_conn, self, table_name)
    def register_column(self, table_name, *col_info):
        self.tables[table_name].add_column(*col_info)
