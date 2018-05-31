from collections import defaultdict
from sakura.daemon.db.table import DBTable
from sakura.daemon.db.grants import register_grant
from sakura.common.io import pack

class DBProber:
    def __init__(self, db):
        self.db = db
        self.driver = db.dbms.driver
    def probe(self):
        print("DB probing startup: %s" % self.db.db_name)
        self.db_conn = self.db.connect()
        self.tables = {}
        self.driver.collect_database_tables(self.db_conn, self)
        self.db_conn.close()
        return self.tables
    def register_table(self, table_name, **metadata):
        #print("DB probing: found table %s" % table_name)
        self.tables[table_name] = DBTable(self.db, table_name, **metadata)
        self.driver.collect_table_columns(self.db_conn, self, table_name)
        self.driver.collect_table_primary_key(self.db_conn, self, table_name)
        self.driver.collect_table_foreign_keys(self.db_conn, self, table_name)
        self.driver.collect_table_count_estimate(self.db_conn, self, table_name)
    def register_column(self, table_name, *col_info, **params):
        #print("----------- found column " + str(col_info))
        self.tables[table_name].add_column(*col_info, **params)
    def register_primary_key(self, table_name, pk_col_names):
        self.tables[table_name].register_primary_key(pk_col_names)
    def register_foreign_key(self, table_name, **fk_info):
        self.tables[table_name].register_foreign_key(**fk_info)
    def register_count_estimate(self, table_name, count_estimate):
        self.tables[table_name].register_count_estimate(count_estimate)

class Database:
    def __init__(self, dbms, db_name, **metadata):
        self.dbms = dbms
        self.db_name = db_name
        self.grants = {}
        self._tables = None
        self.metadata = metadata
    def register_grant(self, db_user, grant):
        register_grant(self.grants, db_user, grant)
    @property
    def tables(self):
        if self._tables is None:
            self.refresh_tables()
        return self._tables
    def connect(self):
        return self.dbms.admin_connect(db_name = self.db_name)
    def refresh_tables(self):
        prober = DBProber(self)
        self._tables = prober.probe()
    def pack(self):
        return pack(dict(
            name = self.db_name,
            tables = self.tables.values(),
            grants = self.grants,
            **self.metadata
        ))
    def overview(self):
        return dict(
            name = self.db_name,
            grants = self.grants
        )
    def create_table(self, table_name, columns, primary_key, foreign_keys):
        db_conn = self.connect()
        self.dbms.driver.create_table(db_conn,
                table_name, columns, primary_key, foreign_keys)
        db_conn.close()
        self.refresh_tables()
    def delete_table(self, table_name):
        db_conn = self.connect()
        self.dbms.driver.delete_table(db_conn, table_name)
        db_conn.close()
        self.refresh_tables()
