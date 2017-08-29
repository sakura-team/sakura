from sakura.daemon.processing.db.column import DBColumn

class DBTable:
    def __init__(self, dbname, table_name):
        self.dbname = dbname
        self.table_name = table_name
        self.columns = []
    def add_column(self, *col_info):
        col = DBColumn(self.table_name, *col_info)
        self.columns.append(col)
