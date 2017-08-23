import psycopg2, uuid, numpy as np
from sakura.daemon.processing.db.column import DBColumn

TABLE_COLS_QUERY = '''
    SELECT  attname,
            format_type(atttypid, atttypmod) AS type,
            col_description(attrelid, attnum) AS comment
    FROM   pg_attribute
    WHERE  attrelid = '%(table_name)s'::regclass::oid
    AND    attnum > 0
    AND    NOT attisdropped
    ORDER  BY attnum;
'''

def timestamp_db_column(table_name, col_name):
    return DBColumn( table_name,
                    col_name,
                    np.float64,
                    'extract(epoch from %s)',
                    'to_timestamp(%s)',
                    ('timestamp',))

def text_db_column(table_name, col_name, max_length):
    return DBColumn( table_name,
                    col_name,
                    (np.str, max_length))

def postgis_geometry_db_column(table_name, col_name, max_length):
    return DBColumn( table_name,
                    col_name,
                    (np.str, max_length),
                    'ST_AsGeoJSON(%s)',
                    'ST_GeomFromGeoJSON(%s)',
                    ('geometry', 'supports_in'))

PG_SIMPLE_TYPES = {
    'timestamp with time zone': timestamp_db_column,
    'integer': lambda table_name, col_name : DBColumn(table_name, col_name, np.int32),
    'bigint': lambda table_name, col_name : DBColumn(table_name, col_name, np.int64)
}

def analyse_col_meta(col_comment):
    col_meta = {}
    if col_comment != None:
        words = col_comment.replace('=', ' ').replace(';', ' ').split()
        if len(words) > 1:
            # analyse words per pair
            for attr, value in zip(words[:-1], words[1:]):
                if attr.startswith('sakura.meta.'):
                    col_meta[attr[12:]] = int(value)
    return col_meta

def analyse_pgtype(table_name, col_name, col_pgtype, col_meta):
    if col_pgtype in PG_SIMPLE_TYPES:
        return PG_SIMPLE_TYPES[col_pgtype](table_name, col_name)
    elif col_pgtype == 'text':
        if 'max_text_chars' in col_meta:
            return text_db_column(table_name, col_name, col_meta['max_text_chars'])
        else:
            raise RuntimeError('Max length of text column %s was not specified!' % col_name)
    elif col_pgtype.startswith('geometry'):
        if 'max_geojson_chars' in col_meta:
            return postgis_geometry_db_column(table_name, col_name, col_meta['max_geojson_chars'])
        else:
            raise RuntimeError('Max geojson length of postgis geometry column %s was not specified!' % col_name)
    else:
        raise RuntimeError('Unknown postgresql type: %s' % col_pgtype)

class PostgreSQLDBDriver:
    @staticmethod
    def describe_table(db_conn, table_name):
        sql = TABLE_COLS_QUERY % dict(table_name = table_name)
        db_columns = []
        with db_conn.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            for col_name, col_pgtype, col_comment in rows:
                col_meta = analyse_col_meta(col_comment)
                db_column = analyse_pgtype(table_name, col_name, col_pgtype, col_meta)
                db_columns.append(db_column)
        return dict(columns = db_columns)
    @staticmethod
    def connect(**db_info):
        return psycopg2.connect(**db_info)
    @staticmethod
    def open_server_cursor(db_conn):
        cursor_name = str(uuid.uuid4()) # unique name
        cursor = db_conn.cursor(name = cursor_name)
        # arraysize: default number of rows when using fetchmany()
        # itersize: default number of rows fetched from the backend
        #           at each network roundtrip (psycopg2-specific)
        cursor.arraysize = cursor.itersize
        return cursor

