import psycopg2, uuid, numpy as np
from collections import defaultdict
from psycopg2.extras import DictCursor

TYPES_SAKURA_TO_PG = {
    'int8':     'smallint',
    'int16':    'smallint',
    'int32':    'integer',
    'int64':    'bigint',
    'float32':  'real',
    'float64':  'double precision',
    'string':   'text',
    'bool':     'boolean',
    'date':     'timestamp with time zone'
}

TYPES_PG_TO_SAKURA = {
    'smallint':                 'int16',
    'integer':                  'int32',
    'bigint':                   'int64',
    'real':                     'float32',
    'double precision':         'float64',
    'text':                     'string',
    'boolean':                  'bool'
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

def register_column(metadata_collector, table_name, col_name, col_pgtype, col_meta, col_pk, col_fk):
    select_clause_wrapper = '"%(table_name)s"."%(col_name)s"'
    value_wrapper = '%s'
    tags = ()
    params = {}
    if col_pgtype.endswith('[]') or col_pgtype in ('hstore', 'json'):
        col_type = 'object'
    elif col_pgtype in ('timestamp with time zone', 'timestamp without time zone', 'date'):
        col_type = 'date'
        select_clause_wrapper = 'extract(epoch from "%(table_name)s"."%(col_name)s") as "%(col_name)s"'
        value_wrapper = 'to_timestamp(%s)'
        tags = ('timestamp',)
    elif col_pgtype.startswith('character') or col_pgtype.startswith('text'):
        col_type = 'string'
        tokens = col_pgtype.split('(')
        if len(tokens) == 1:
            params.update(max_length = col_meta.get('max_text_chars', None))
        else:
            params.update(max_length = int(tokens[1][:-1]))
    elif col_pgtype.startswith('geometry'):
        col_type = 'geometry'
        params.update(max_length = col_meta.get('max_geojson_chars', None))
        select_clause_wrapper = 'ST_AsGeoJSON("%(table_name)s"."%(col_name)s") as "%(col_name)s"'
        value_wrapper = 'ST_GeomFromGeoJSON(%s)'
        tags = ('geometry', 'supports_in')
    elif col_pgtype in TYPES_PG_TO_SAKURA.keys():
        col_type = TYPES_PG_TO_SAKURA[col_pgtype]
    else:
        raise RuntimeError('Unknown postgresql type: %s' % col_pgtype)
    metadata_collector.register_column(
            table_name, col_name, col_type,
            select_clause_wrapper, value_wrapper,
            tags, col_pk, col_fk, **params)

SQL_GET_DS_USERS = '''\
SELECT  usename, usecreatedb FROM pg_user;
'''

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

# note: we do not handle foreign key definitions spanning on several columns...
SQL_GET_TABLE_COLUMNS = '''
    WITH    pk_attnums AS (
                SELECT unnest(indkey) as pk_attnum
                FROM pg_index
                WHERE pg_index.indrelid = '"%(table_name)s"'::regclass::oid
                AND indisprimary),
            fk_info AS (
                SELECT r.conkey[1] as attnum, c.relname as fk_table, fk_a.attname as fk_attname
                FROM pg_catalog.pg_constraint r, pg_attribute fk_a, pg_catalog.pg_class c
                WHERE r.conrelid = '"%(table_name)s"'::regclass
                AND r.contype = 'f'
                AND fk_a.attrelid = r.confrelid
                AND fk_a.attnum = r.confkey[1]
                AND r.confrelid = c.oid
            )
    SELECT  a.attname,
            format_type(a.atttypid, a.atttypmod) AS type,
            col_description(a.attrelid, a.attnum) AS comment,
            a.attnum IN (SELECT pk_attnum FROM pk_attnums) as pk,
            fk.fk_table,
            fk.fk_attname
    FROM   pg_attribute a
    LEFT JOIN fk_info fk
        ON fk.attnum = a.attnum
    WHERE  a.attrelid = '"%(table_name)s"'::regclass::oid
    AND    a.attnum > 0
    AND    NOT a.attisdropped
    ORDER  BY a.attnum;
'''

SQL_CREATE_DB = '''
CREATE DATABASE "%(db_name)s" WITH OWNER "%(db_owner)s";
'''

SQL_GRANT_DB = '''
GRANT ALL ON DATABASE "%(db_name)s" TO "%(db_owner)s";
REVOKE ALL ON DATABASE "%(db_name)s" FROM PUBLIC;
'''

SQL_DESC_COLUMN = '"%(col_name)s" %(col_type)s'
SQL_FK = ' REFERENCES "%(table_name)s" ("%(col_name)s")'
SQL_CREATE_TABLE = '''
CREATE TABLE "%(table_name)s" (%(columns_sql)s);
'''

DEFAULT_CONNECT_TIMEOUT = 4     # seconds

class PostgreSQLDBDriver:
    NAME = 'postgresql'
    @staticmethod
    def connect(**kwargs):
        # if database is not specified, connect to 'postgres' db
        if 'dbname' not in kwargs:
            kwargs['dbname'] = 'postgres'
        if 'connect_timeout' not in kwargs:
            kwargs['connect_timeout'] = DEFAULT_CONNECT_TIMEOUT
        conn = psycopg2.connect(**kwargs)
        conn.cursor_factory = DictCursor
        return conn
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
    def collect_users(admin_db_conn, metadata_collector):
        with admin_db_conn.cursor() as cursor:
            cursor.execute(SQL_GET_DS_USERS)
            for row in cursor:
                metadata_collector.register_user(
                        row['usename'], row['usecreatedb'])
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
            for col_name, col_pgtype, col_comment, col_pk, \
                    col_fk_table, col_fk_attname in rows:
                if col_fk_table is None:
                    col_fk = None
                else:
                    col_fk = (col_fk_table, col_fk_attname)
                col_meta = analyse_col_meta(col_comment)
                register_column(metadata_collector,
                    table_name, col_name, col_pgtype, col_meta, col_pk, col_fk)
    @staticmethod
    def create_db(admin_db_conn, db_name, db_owner):
        # CREATE DATABASE requires to set autocommit, and
        # cannot be execute in a multiple-statements string
        saved_mode = admin_db_conn.autocommit
        admin_db_conn.autocommit = True
        with admin_db_conn.cursor() as cursor:
            for sql in (SQL_CREATE_DB, SQL_GRANT_DB):
                cursor.execute(sql % dict(
                        db_name = db_name,
                        db_owner = db_owner))
        admin_db_conn.autocommit = saved_mode
    @staticmethod
    def create_table(db_conn, table_name, columns):
        pk = tuple(col_name for col_name, col_type, col_pk, col_fk_info \
                            in columns if col_pk)
        columns_sql = []
        for col_name, col_type, col_pk, col_fk_info in columns:
            col_sql = SQL_DESC_COLUMN % dict(
                col_name = col_name,
                col_type = TYPES_SAKURA_TO_PG[col_type]
            )
            if col_pk and len(pk) == 1:
                col_sql += ' PRIMARY KEY'
            if col_fk_info is not None:
                fk_table_name, fk_col_name = col_fk_info
                col_sql += SQL_FK % dict(
                    table_name = fk_table_name,
                    col_name = fk_col_name
                )
            columns_sql.append(col_sql)
        if len(pk) > 1:
            escaped_pk_cols = tuple('"%s"' % col_name for col_name in pk)
            constraint_sql = "PRIMARY KEY (" + ', '.join(escaped_pk_cols) + ")"
            columns_sql.append(constraint_sql)
        sql = SQL_CREATE_TABLE % dict(
            table_name = table_name,
            columns_sql = ', '.join(columns_sql)
        )
        with db_conn.cursor() as cursor:
            cursor.execute(sql)
        db_conn.commit()
    @staticmethod
    def add_rows(db_conn, table_name, value_wrappers, rows):
        if len(rows) == 0:
            return  # nothing to do
        tuple_pattern = '(' + ','.join(value_wrappers) + ')'
        with db_conn.cursor() as cursor:
            args_str = b','.join(cursor.mogrify(tuple_pattern, row) for row in rows)
            cursor.mogrify('"%s"' % table_name)
            cursor.execute(b"INSERT INTO " + cursor.mogrify('"%s"' % table_name) + \
                           b" VALUES " + args_str)
        db_conn.commit()

DRIVER = PostgreSQLDBDriver

