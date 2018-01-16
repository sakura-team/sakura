from collections import defaultdict
from sakura.daemon.db.table import DBTable

class DBProber:
    def __init__(self, db):
        self.db = db
        self.driver = db.dbms.driver
    def probe(self):
        self.db_conn = self.db.connect()
        self.tables = {}
        self.driver.collect_db_tables(self.db_conn, self)
        self.db_conn.close()
        return self.tables
    def register_table(self, table_name):
        print("DB probing: found table %s" % table_name)
        self.tables[table_name] = DBTable(self.db, table_name)
        self.driver.collect_table_columns(self.db_conn, self, table_name)
    def register_column(self, table_name, *col_info, **params):
        print("----------- found column " + str(col_info))
        self.tables[table_name].add_column(*col_info, **params)

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
        if user is None:
            dbuser = 'sakura_' + tuple(self.users.keys())[0]
        else:
            dbuser = 'sakura_' + user
        if password is None:
            password = dbuser
        return self.dbms.driver.connect(
            host     = self.dbms.host,
            dbname   = self.db_name,
            user     = dbuser,
            password = password
        )
    def refresh_tables(self):
        prober = DBProber(self)
        self._tables = prober.probe()
    def pack(self):
        return dict(
            name = self.db_name,
            owner = self.owner,
            tables = self.tables.values(),
            users = self.users
        )
    def overview(self):
        return dict(
            name = self.db_name,
            owner = self.owner,
            users = self.users
        )
    def create_table(self, user, passwd, table_name, columns):
        db_conn = self.connect(user, passwd)
        self.dbms.driver.create_table(db_conn, table_name, columns)
        db_conn.close()
        self.refresh_tables()
