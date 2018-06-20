from sakura.daemon.db.column import DBColumn
from sakura.daemon.processing.stream import SQLTableStream
from sakura.daemon.csvtools import stream_csv

class DBTable:
    def __init__(self, db, table_name):
        self.db = db
        self.name = table_name
        self.columns = []
        self.primary_key = []
        self.foreign_keys = []
        self.count_estimate = 0
        self._stream = None
    @property
    def stream(self):
        if self._stream is None:
            self._stream = SQLTableStream(self.name, self)
        return self._stream
    def add_column(self, *col_info, **params):
        col = DBColumn(self.name, *col_info, **params)
        self.columns.append(col)
    def pack(self):
        return dict(name = self.name, columns = self.columns,
                    primary_key = self.primary_key,
                    foreign_keys = self.foreign_keys,
                    count_estimate = self.count_estimate)
    def get_range(self, row_start, row_end):
        return self.stream.get_range(row_start, row_end)
    def add_rows(self, rows):
        value_wrappers = tuple(col.value_wrapper for col in self.columns)
        with self.db.connect() as db_conn:
            self.db.dbms.driver.add_rows(db_conn, self.name, value_wrappers, rows)
    def register_primary_key(self, pk_col_names):
        self.primary_key = pk_col_names
    def register_foreign_key(self, **fk_info):
        self.foreign_keys.append(fk_info)
    def register_count_estimate(self, count_estimate):
        self.count_estimate = count_estimate
    def get_count_estimate(self):
        return self.count_estimate
    def stream_csv(self, gzip_compression=False):
        header_labels = tuple(col.col_name for col in self.columns)
        stream = self.stream.chunks()
        yield from stream_csv(
                    header_labels, stream, gzip_compression)
