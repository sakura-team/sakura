from sakura.common.chunk import NumpyChunk
from sakura.daemon.processing.sources.base import SourceBase
from sakura.daemon.db.query import SQLQuery

class SQLSourceIterator:
    def __init__(self, stream, chunk_size, offset):
        self.chunk_size = chunk_size
        self.dtype = stream.get_dtype()
        self.released = False
        self.db_conn = stream.db.connect()
        self.cursor = stream.open_cursor(self.db_conn, offset)
        if self.chunk_size == None:
            self.chunk_size = self.cursor.arraysize
    def __iter__(self):
        return self
    def __next__(self):
        if self.released:
            raise StopIteration
        chunk_data = self.cursor.fetchmany(self.chunk_size)
        if len(chunk_data) < self.chunk_size:
            # less data than expected => end of stream
            self.release()
        if len(chunk_data) == 0:
            raise StopIteration
        return NumpyChunk.create(chunk_data, self.dtype)
    def release(self):
        if not self.released:
            self.cursor.close()
            self.db_conn.close()
            self.released = True
    def __del__(self):
        self.release()

class SQLSource(SourceBase):
    def __init__(self, label, query, db):
        SourceBase.__init__(self, label)
        self.db = db
        self.query = query
        for col in query.selected_cols:
            self.add_column(col.col_name, col.np_dtype, col.tags)
    def __iter__(self):
        for chunk in self.chunks():
            yield from chunk
    def chunks(self, chunk_size = None, offset=0):
        return SQLSourceIterator(self, chunk_size, offset)
    def __select_columns__(self, *col_indexes):
        new_query = self.query.select_columns(*col_indexes)
        return SQLSource(self.label, new_query, self.db)
    def __filter__(self, *cond_info):
        new_query = self.query.filter(*cond_info)
        return SQLSource(self.label, new_query, self.db)
    def open_cursor(self, db_conn, offset=0):
        self.query.set_offset(offset)
        cursor = self.db.dbms.driver.open_server_cursor(db_conn)
        self.query.execute(cursor)
        return cursor

class SQLTableSource(SQLSource):
    def __init__(self, label, db_table):
        query = SQLQuery(db_table.columns, ())
        SQLSource.__init__(self, label, query, db_table.db)
