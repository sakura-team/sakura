import psycopg2, uuid, numpy as np
from collections import defaultdict
from sakura.daemon.processing.db import drivers

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

def register_column(metadata_collector, table_name, col_name, col_pgtype, col_meta):
    if col_pgtype == 'timestamp with time zone':
        metadata_collector.register_column(
                    table_name,
                    col_name,
                    np.float64,
                    'extract(epoch from %s)',
                    'to_timestamp(%s)',
                    ('timestamp',))
    elif col_pgtype == 'integer':
        metadata_collector.register_column(table_name, col_name, np.int32)
    elif col_pgtype == 'bigint':
        metadata_collector.register_column(table_name, col_name, np.int64)
    elif col_pgtype.startswith('character varying('):
        max_length = int(col_pgtype[18:-1])
        metadata_collector.register_column(table_name, col_name, (np.str, max_length))
    elif col_pgtype in ('text', 'character varying'):
        max_length = col_meta.get('max_text_chars', None)
        if max_length is None:
            raise RuntimeError('Max length of text column %s was not specified!' % col_name)
        metadata_collector.register_column(table_name, col_name, (np.str, max_length))
    elif col_pgtype.startswith('geometry'):
        max_length = col_meta.get('max_geojson_chars', None)
        if max_length is None:
            raise RuntimeError('Max geojson length of postgis geometry column %s was not specified!' % col_name)
        metadata_collector.register_column(
                table_name, col_name, (np.str, max_length),
                'ST_AsGeoJSON(%s)', 'ST_GeomFromGeoJSON(%s)',
                ('geometry', 'supports_in'))
    else:
        raise RuntimeError('Unknown postgresql type: %s' % col_pgtype)

SQL_GET_DBS = '''\
SELECT  datname  FROM pg_database;
'''

SQL_GET_DB_ACCESS_GRANTS = '''\
SELECT  CASE WHEN user_oid = 0 THEN 'public' ELSE pg_catalog.pg_get_userbyid(user_oid) END,
        datname, privilege_type
FROM
    (
        SELECT  (aclexplode(datacl)).grantee AS user_oid,
                (aclexplode(datacl)).privilege_type,
                datname
        FROM pg_database
        UNION
        SELECT  datdba,
                'OWNER',
                datname
        FROM pg_database
    ) AS dbpriv
WHERE dbpriv.privilege_type IN ('CREATE', 'CONNECT', 'OWNER');
'''

SQL_GET_DB_TABLES = '''\
SELECT c.relname as "Name"
FROM pg_catalog.pg_class c
     LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind = 'r'
      AND n.nspname <> 'pg_catalog'
      AND n.nspname <> 'information_schema'
      AND n.nspname !~ '^pg_toast'
      AND pg_catalog.pg_table_is_visible(c.oid)
      AND c.relname !~ '^_';
'''

SQL_GET_TABLE_COLUMNS = '''
    SELECT  attname,
            format_type(atttypid, atttypmod) AS type,
            col_description(attrelid, attnum) AS comment
    FROM   pg_attribute
    WHERE  attrelid = '%(table_name)s'::regclass::oid
    AND    attnum > 0
    AND    NOT attisdropped
    ORDER  BY attnum;
'''

DEFAULT_CONNECT_TIMEOUT = 4     # seconds

class PostgreSQLDBDriver:
    NAME = 'postgresql'
    @staticmethod
    def connect(**kwargs):
        if 'connect_timeout' not in kwargs:
            kwargs['connect_timeout'] = DEFAULT_CONNECT_TIMEOUT
        return psycopg2.connect(**kwargs)
    @staticmethod
    def open_server_cursor(db_conn):
        cursor_name = str(uuid.uuid4()) # unique name
        cursor = db_conn.cursor(name = cursor_name)
        # arraysize: default number of rows when using fetchmany()
        # itersize: default number of rows fetched from the backend
        #           at each network roundtrip (psycopg2-specific)
        cursor.arraysize = cursor.itersize
        return cursor
    @staticmethod
    def get_current_db_name(db_conn):
        with db_conn.cursor() as cursor:
            cursor.execute('''SELECT current_database();''')
            return cursor.fetchone()[0]
    @staticmethod
    def collect_dbs(admin_db_conn, metadata_collector):
        with admin_db_conn.cursor() as cursor:
            cursor.execute(SQL_GET_DBS)
            for row in cursor:
                dbname = row[0]
                metadata_collector.register_db(dbname)
    @staticmethod
    def collect_db_grants(admin_db_conn, metadata_collector):
        # we must tell metadata_visitor which user has READ, WRITE, OWNER
        # access to which database
        with admin_db_conn.cursor() as cursor:
            cursor.execute(SQL_GET_DB_ACCESS_GRANTS)
            for dbuser, dbname, privtype in cursor:
                privtype = { 'CONNECT': 'READ', 'CREATE': 'WRITE', 'OWNER': 'OWNER' }[privtype]
                metadata_collector.register_grant(dbuser, dbname, privtype)
    @staticmethod
    def collect_db_tables(db_conn, metadata_collector):
        # db_conn must be connected to the targeted database
        with db_conn.cursor() as cursor:
            cursor.execute(SQL_GET_DB_TABLES)
            for row in cursor:
                tablename = row[0]
                metadata_collector.register_table(tablename)
    @staticmethod
    def collect_table_columns(db_conn, metadata_collector, table_name):
        sql = SQL_GET_TABLE_COLUMNS % dict(table_name = table_name)
        with db_conn.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            for col_name, col_pgtype, col_comment in rows:
                col_meta = analyse_col_meta(col_comment)
                register_column(metadata_collector,
                    table_name, col_name, col_pgtype, col_meta)

drivers.register(PostgreSQLDBDriver)
