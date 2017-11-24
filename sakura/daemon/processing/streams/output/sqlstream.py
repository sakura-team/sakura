import numpy as np
from sakura.common.chunk import NumpyChunk
from sakura.daemon.processing.streams.output.base import OutputStreamBase
from sakura.daemon.db.query import SQLQuery

class SQLStream(OutputStreamBase):
    def __init__(self, label, query, db_conn, db_driver):
        OutputStreamBase.__init__(self, label)
        self.db_driver = db_driver
        self.db_conn = db_conn
        self.open_cursors = set()
        self.query = query
        for col in query.selected_cols:
            self.add_column(col.col_name, col.np_dtype, col.tags)
    def __iter__(self):
        for chunk in self.chunks():
            yield from chunk
    def chunks(self, chunk_size = None, offset=0):
        self.query.set_offset(offset)
        cursor = self.open_cursor()
        self.query.execute(cursor)
        if chunk_size == None:
            chunk_size = cursor.arraysize
        while True:
            rowlist = list(tuple(row) for row in cursor.fetchmany(chunk_size))
            if len(rowlist) == 0:
                break
            yield np.array(rowlist, self.get_dtype()).view(NumpyChunk)
        self.close_cursor(cursor)
    def __select_columns__(self, *col_indexes):
        new_query = self.query.select_columns(*col_indexes)
        return SQLStream(self.label, new_query, self.db_conn, self.db_driver)
    def __filter__(self, *cond_info):
        new_query = self.query.filter(*cond_info)
        return SQLStream(self.label, new_query, self.db_conn, self.db_driver)
    def open_cursor(self):
        cursor = self.db_driver.open_server_cursor(self.db_conn)
        self.open_cursors.add(cursor)
        return cursor
    def close_cursor(self, cursor):
        cursor.close()
        self.open_cursors.remove(cursor)
    def __del__(self):
        for cursor in self.open_cursors:
            cursor.close()

class SQLTableStream(SQLStream):
    def __init__(self, label, db_table, user, passwd):
        query = SQLQuery(db_table.columns, ())
        self.db_conn = db_table.db.connect(user, passwd)
        SQLStream.__init__(self, label, query, self.db_conn, db_table.db.dbms.driver)
