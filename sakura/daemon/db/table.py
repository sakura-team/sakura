from sakura.daemon.db.column import DBColumn
from sakura.daemon.processing.stream import SQLTableStream

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
    def get_range(self, user, passwd, row_start, row_end):
        stream = SQLTableStream(self.name, self, user, passwd)
        return stream.get_range(row_start, row_end)
