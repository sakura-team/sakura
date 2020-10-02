from sakura.daemon.db.column import DBColumn
from sakura.daemon.processing.source import SQLTableSource
from sakura.daemon.csvtools import stream_csv

class DBTable:
    def __init__(self, db, table_name):
        self.db = db
        self.name = table_name
        self.columns = []
        self.primary_key = []
        self.foreign_keys = []
        self.count_estimate = 0
        self._source = None
    def source(self):
        if self._source is None:
            self._source = SQLTableSource(self.name, self)
        return self._source
    def add_column(self, *col_info, **params):
        col = DBColumn(self, *col_info, **params)
        self.columns.append(col)
    def pack(self):
        return dict(name = self.name, columns = self.columns,
                    primary_key = self.primary_key,
                    foreign_keys = self.foreign_keys,
                    count_estimate = self.count_estimate)
    def get_range(self, row_start, row_end):
        return self.source().get_range(row_start, row_end)
    def chunks(self, allow_approximate = False):
        return self.source().chunks(allow_approximate = allow_approximate)
    def get_dtype(self):
        return self.source().get_dtype()
    def add_rows(self, rows):
        with self.db.connect() as db_conn:
            self.db.dbms.driver.add_rows(db_conn, self.name, self.columns, rows)
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
        stream = self.source().chunks()
        yield from stream_csv(
                    header_labels, stream, gzip_compression)
    @property
    def col_tags_info(self):
        if self.name not in self.db.col_tags_info:
            self.db.col_tags_info[self.name] = [()] * len(self.columns)
        return self.db.col_tags_info[self.name]
    def set_col_tags(self, col_tags_info):
        self.db.col_tags_info[self.name] = col_tags_info
