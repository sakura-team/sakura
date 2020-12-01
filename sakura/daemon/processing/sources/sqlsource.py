import traceback, greenlet
from time import time
from sakura.common.chunk import NumpyChunk
from sakura.common.exactness import EXACT
from sakura.daemon.processing.sources.base import SourceBase
from sakura.common.ops import LOWER, LOWER_OR_EQUAL, GREATER, GREATER_OR_EQUAL, IN, EQUALS, NOT_EQUALS
from sakura.daemon.processing.geo import GeoBoundingBox
from sakura.daemon.db import CURSOR_MODE, DEFAULT_FIRST_FETCH

DEBUG = False
PRINT_SQL = True

COMP_OP_TO_SQL_SPECIAL = {
    (EQUALS, None):     'IS NULL',
    (NOT_EQUALS, None): 'IS NOT NULL'
}

COMP_OP_TO_SQL = {
    LOWER:              '<',
    LOWER_OR_EQUAL:     '<=',
    EQUALS:             '=',
    NOT_EQUALS:         '!=',
    GREATER:            '>',
    GREATER_OR_EQUAL:   '>='
}

CHUNK_DELAY_LOW_LIMIT = 0.5
CHUNK_DELAY_HIGH_LIMIT = 1.0

class SQLSourceIterator:
    def __init__(self, source, chunk_size, profile):
        self.dtype = source.get_dtype()
        sql_text, values = source.to_sql()
        if PRINT_SQL:
            print(sql_text, values)
        self.db_conn = source.connect()
        self.cursor = self.db_conn.cursor(
            cursor_mode = CURSOR_MODE.SERVER,
            profile = profile,
            profile_query = (sql_text, values)
        )
        # execute the real query
        self.cursor.execute(sql_text, values)
        if chunk_size is None:
            self.fetch_size = DEFAULT_FIRST_FETCH
            self.adapt_fetch_size = True
        else:
            self.fetch_size = chunk_size
            self.adapt_fetch_size = False
    @property
    def released(self):
        return self.cursor is None
    def __iter__(self):
        return self
    def __next__(self):
        if self.released:
            raise StopIteration
        if self.adapt_fetch_size:
            prev_time = time()
        try:
            chunk_data = self.cursor.fetchmany(self.fetch_size)
        except greenlet.GreenletExit:
            raise
        except:
            print('Exception in sql source iterator')
            traceback.print_exc()
            # connection was probably cancelled, end
            chunk_data = []
        if len(chunk_data) < self.fetch_size:
            # less data than expected => end of stream
            if DEBUG:
                print('sql source: end of data', self.db_conn)
            self.cursor = None
            self.db_conn = None
        if len(chunk_data) == 0:
            raise StopIteration
        if self.adapt_fetch_size:
            # adapt next fetch_size to performance
            chunk_delay = time() - prev_time
            if chunk_delay < CHUNK_DELAY_LOW_LIMIT:
                self.fetch_size *= 2
                if DEBUG:
                    print('fetch_size', self.fetch_size, self.db_conn)
            if chunk_delay > CHUNK_DELAY_HIGH_LIMIT:
                self.fetch_size = self.fetch_size // 4
                # ensure new fetch_size is not zero
                self.fetch_size = max(1, self.fetch_size)
                if DEBUG:
                    print('fetch_size', self.fetch_size, self.db_conn)
        return NumpyChunk.create(chunk_data, self.dtype, EXACT)

class SQLDatabaseSource(SourceBase):
    def __init__(self, label, db = None, db_columns = None):
        SourceBase.__init__(self, label)
        if db_columns is not None:
            self.data.db = db
            # auto populate source columns
            for db_col in db_columns:
                col = self.add_column(db_col.col_name, db_col.col_type, db_col.tags,
                                      **db_col.col_type_params)
                # link db_col in each generic source column object
                col.data.db_col = db_col
                for subcol, db_subcol in zip(col.subcolumns, db_col.subcolumns):
                    subcol.data.db_col = db_subcol
    def connect(self, reuse_conn = None):
        return self.data.db.connect(reuse_conn = reuse_conn)
    def all_chunks(self, chunk_size = None, profile = 'interactive'):
        return SQLSourceIterator(self, chunk_size, profile)
    def merge_in_bbox_row_filters(self, db_row_filters):
        bbox_per_column = {}
        other_row_filters = []
        for db_row_filter in db_row_filters:
            db_column, comp_op, value = db_row_filter
            if comp_op is IN:
                bbox = bbox_per_column.get(db_column)
                if bbox is None:
                    bbox = value
                else:
                    bbox = bbox.intersect(value)
                bbox_per_column[db_column] = bbox
            else:
                other_row_filters.append(db_row_filter)
        bbox_row_filters = ((db_column, IN, bbox) for db_column, bbox in bbox_per_column.items())
        return tuple(other_row_filters) + tuple(bbox_row_filters)
    def to_sql(self):
        selected_db_cols = tuple(col.data.db_col for col in self.columns)
        db_row_filters = tuple((col.data.db_col, comp_op, other) for col, comp_op, other in self.row_filters)
        db_row_filters = self.merge_in_bbox_row_filters(db_row_filters)
        db_join_conds = tuple((left_col.data.db_col, right_col.data.db_col) for left_col, right_col in self.join_conds)
        select_clause = 'SELECT ' + ', '.join(db_col.to_sql_select_clause() for db_col in selected_db_cols)
        tables = set(db_col.table.name for db_col in selected_db_cols)
        tables |= set(f[0].table.name for f in db_row_filters)
        from_clause = 'FROM "' + '", "'.join(tables) + '"'
        where_clause, sort_clause, offset_clause, limit_clause, filter_vals = '', '', '', '', ()
        cond_texts, cond_vals = (), ()
        for db_row_filter in db_row_filters:
            cond_info = self.db_row_filter_to_sql(db_row_filter)
            cond_texts += cond_info[0]
            cond_vals += cond_info[1]
        cond_texts += tuple(self.db_join_cond_to_sql(db_join_cond) for db_join_cond in db_join_conds)
        if len(cond_texts) > 0:
            where_clause = 'WHERE ' + ' AND '.join(cond_texts)
        if len(self.sort_columns) > 0:
            sort_db_cols = tuple(col.data.db_col for col in self.sort_columns)
            sort_clause = "ORDER BY " + ', '.join(db_col.to_sql_sort_clause() for db_col in sort_db_cols)
        if self._offset > 0:
            offset_clause = "OFFSET " + str(self._offset)
        if self._limit is not None:
            limit_clause = "LIMIT " + str(self._limit)
        sql_text = ' '.join((select_clause, from_clause, where_clause, sort_clause, offset_clause, limit_clause))
        return (sql_text, cond_vals)
    def db_join_cond_to_sql(self, db_join_cond):
        db_left_col, db_right_col = db_join_cond
        return db_left_col.to_sql_where_clause() + ' = ' + db_right_col.to_sql_where_clause()
    def db_row_filter_to_sql(self, db_row_filter):
        db_column, comp_op, value = db_row_filter
        col_name = db_column.to_sql_where_clause()
        op_sql_special = COMP_OP_TO_SQL_SPECIAL.get((comp_op, value), None)
        if op_sql_special != None:
            sql = col_name + ' ' + op_sql_special
            return (sql,), ()
        if comp_op is IN and isinstance(value, GeoBoundingBox):
            sql = 'ST_Contains(' + db_column.value_wrapper + ', ' + col_name + ')'
            value = value.as_geojson()
        else:
            op_sql = COMP_OP_TO_SQL.get(comp_op, None)
            if op_sql is None:
                op_sql = getattr(comp_op, 'SQL_OP', None)
            assert op_sql != None, ("Don't know how to write %s as an SQL operator." % str(comp_op))
            sql = col_name + ' ' + op_sql + ' ' + db_column.value_wrapper
        return (sql,), (value,)
    def get_native_join_id(self):
        return ('SQLDatabaseSource', self.data.db.unique_id())

class SQLTableSource:
    def __new__(cls, label, db_table = None):
        if db_table is not None:
            return SQLDatabaseSource(label, db_table.db, db_table.columns)
        else:
            return SQLDatabaseSource(label)
