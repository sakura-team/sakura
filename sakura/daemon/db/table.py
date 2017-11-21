from sakura.daemon.db.column import DBColumn

class DBTable:
    def __init__(self, db, table_name):
        self.db = db
        self.name = table_name
        self.columns = []
    def add_column(self, *col_info):
        col = DBColumn(self.name, *col_info)
        self.columns.append(col)
    def pack(self):
        return dict(name = self.name, columns = self.columns)
