from collections import defaultdict
from sakura.daemon.db.table import DBTable

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
        print("----------- found column " + str(col_info))
        self.tables[table_name].add_column(*col_info)

class Database:
    def __init__(self, dbms, db_name):
        self.dbms = dbms
        self.db_name = db_name
        self.owner = None
        self.users = defaultdict(lambda: dict(READ=False, WRITE=False))
        self._tables = None
    @property
    def tables(self):
        if self._tables is None:
            self.refresh_tables()
        return self._tables
    def grant(self, user, privtype):
        if privtype == 'OWNER':
            self.owner = user
        else:
            self.users[user][privtype] = True
    def connect(self, user = None, password = None):
        # TODO correctly pass user credentials up to here
        # for now we just select the first user and consider
        # password is the same as username
        dbuser = 'sakura_' + tuple(self.users.keys())[0]
        password = dbuser
        print(dict(
            dbname=self.db_name, user=dbuser, password=password
        ))
        return self.dbms.driver.connect(
            host     = self.dbms.host,
            dbname   = self.db_name,
            user     = dbuser,
            password = password
        )
    def refresh_tables(self):
        db_conn = self.connect()
        prober = DBProber(self.dbms.driver, db_conn)
        self._tables = prober.probe()
        db_conn.close()
    def pack(self):
        return dict(
            db_name = self.db_name,
            owner = self.owner,
            tables = self.tables.values(),
            users = self.users
        )
    def overview(self):
        return dict(
            db_name = self.db_name,
            owner = self.owner,
            users = self.users
        )
