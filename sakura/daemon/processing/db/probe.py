from sakura.daemon.processing.db.table import DBTable

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
