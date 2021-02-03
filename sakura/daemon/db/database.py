from collections import defaultdict
from sakura.daemon.db.table import DBTable
from sakura.daemon.db.grants import register_grant
from sakura.common.io import pack
from sakura.daemon.db import CURSOR_MODE
from gevent.lock import Semaphore

class DBProber:
    def __init__(self, db):
        self.db = db
        self.driver = db.dbms.driver
    def probe(self):
        print("DB probing startup: %s" % self.db.db_name)
        db_conn = self.db.connect()
        tables_metadata = self.driver.probe_database(db_conn)
        db_conn.close()
        self.tables = { table_name: DBTable(self.db, table_name, **tb_metadata) \
                        for table_name, tb_metadata in tables_metadata.items() }
        return self.tables

class Database:
    def __init__(self, dbms, db_name, **metadata):
        self.dbms = dbms
        self.db_name = db_name
        self.grants = {}
        self._tables = None
        self.metadata = metadata
        self.probing_lock = Semaphore()
    def unique_id(self):
        return ('Database', self.db_name, self.dbms.unique_id())
    def register_grant(self, db_user, grant):
        register_grant(self.grants, db_user, grant)
    @property
    def tables(self):
        with self.probing_lock:
            if self._tables is None:
                self.refresh_tables()
        return self._tables
    def connect(self, reuse_conn = None):
        return self.dbms.admin_connect(db_name = self.db_name,
                                       reuse_conn = reuse_conn)
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
    @property
    def col_tags_info(self):
        if self.db_name not in self.dbms.col_tags_info:
            self.dbms.col_tags_info[self.db_name] = {}
        return self.dbms.col_tags_info[self.db_name]
