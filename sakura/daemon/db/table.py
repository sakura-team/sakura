from sakura.daemon.db.column import DBColumn

class DBTable:
    def __init__(self, dbname, table_name):
        self.dbname = dbname
        self.name = table_name
        self.columns = []
    def add_column(self, *col_info):
        col = DBColumn(self.name, *col_info)
        self.columns.append(col)
    def summarize(self):
        return dict(name = self.name, columns = self.columns)
