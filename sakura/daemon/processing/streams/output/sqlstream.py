import numpy as np
from sakura.common.chunk import NumpyChunk
from sakura.daemon.processing.streams.output.base import OutputStreamBase
from sakura.daemon.db.query import SQLQuery

class SQLStreamIterator:
    def __init__(self, stream, chunk_size, offset):
        self.cursor = stream.open_cursor(offset)
        self.chunk_size = chunk_size
        if self.chunk_size == None:
            self.chunk_size = self.cursor.arraysize
        self.dtype = stream.get_dtype()
        self.released = False
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
            print('cursor released')
            self.cursor.close()
            self.released = True
    def __del__(self):
        print('SQLStreamIterator.__del__')
        self.release()

class SQLStream(OutputStreamBase):
    def __init__(self, label, query, db_conn, db_driver):
        OutputStreamBase.__init__(self, label)
        self.db_driver = db_driver
        self.db_conn = db_conn
        self.query = query
        for col in query.selected_cols:
            self.add_column(col.col_name, col.np_dtype, col.tags)
    def __iter__(self):
        for chunk in self.chunks():
            yield from chunk
    def chunks(self, chunk_size = None, offset=0):
        return SQLStreamIterator(self, chunk_size, offset)
    def __select_columns__(self, *col_indexes):
        new_query = self.query.select_columns(*col_indexes)
        return SQLStream(self.label, new_query, self.db_conn, self.db_driver)
    def __filter__(self, *cond_info):
        new_query = self.query.filter(*cond_info)
        return SQLStream(self.label, new_query, self.db_conn, self.db_driver)
    def open_cursor(self, offset=0):
        self.query.set_offset(offset)
        cursor = self.db_driver.open_server_cursor(self.db_conn)
        self.query.execute(cursor)
        return cursor

class SQLTableStream(SQLStream):
    def __init__(self, label, db_table):
        query = SQLQuery(db_table.columns, ())
        self.db_conn = db_table.db.connect()
        SQLStream.__init__(self, label, query, self.db_conn, db_table.db.dbms.driver)
