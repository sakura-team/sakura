import psycopg2, uuid, numpy as np
from collections import defaultdict
from psycopg2.extras import DictCursor
from sakura.common.errors import APIRequestError
from sakura.common.access import GRANT_LEVELS

DEBUG_CURSORS=False
#DEBUG_CURSORS=True

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

IGNORED_DATABASES = ('template0', 'template1', 'postgres')

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
            tags, **params)

SQL_GET_DS_GRANTS = '''\
SELECT  usename, usecreatedb FROM pg_user;
'''

SQL_SET_DS_GRANTS = '''\
ALTER ROLE %(ds_user)s WITH %(ds_grants)s;
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

SQL_GET_TABLE_COLUMNS = '''
    SELECT  a.attname,
            format_type(a.atttypid, a.atttypmod) AS type,
            col_description(a.attrelid, a.attnum) AS comment
    FROM   pg_attribute a
    WHERE  a.attrelid = '"%(table_name)s"'::regclass::oid
    AND    a.attnum > 0
    AND    NOT a.attisdropped
    ORDER  BY a.attnum;
'''

SQL_GET_TABLE_FOREIGN_KEYS = '''
    WITH fk_info AS (
        SELECT  unnest(r.conkey) as attnum,
                unnest(r.confkey) as fk_attnum,
                r.oid,
                fk_table.relname as fk_table,
                fk_table.oid as fk_table_oid
        FROM    pg_catalog.pg_constraint r,
                pg_catalog.pg_class fk_table
        WHERE   r.conrelid = '"%(table_name)s"'::regclass
          AND   r.contype = 'f'
          AND   r.confrelid = fk_table.oid)
    SELECT  json_agg(a.attname) as attnames,
            json_agg(fk_a.attname) as fk_attnames,
            fk.fk_table
    FROM    pg_attribute a, pg_attribute fk_a, fk_info fk
    WHERE   a.attrelid = '"%(table_name)s"'::regclass
      AND   a.attnum = fk.attnum
      AND   fk_a.attrelid = fk.fk_table_oid
      AND   fk_a.attnum = fk.fk_attnum
    GROUP BY fk.oid, fk.fk_table;
'''

SQL_GET_TABLE_PRIMARY_KEY = '''
    WITH pk_info AS (
        SELECT  unnest(indkey) as attnum
        FROM    pg_index
        WHERE   pg_index.indrelid = '"%(table_name)s"'::regclass::oid
        AND     indisprimary)
    SELECT  COALESCE(json_agg(a.attname), '[]') as attnames
    FROM pg_attribute a, pk_info pk
    WHERE a.attrelid = '"%(table_name)s"'::regclass
      AND a.attnum = pk.attnum;
'''

SQL_CREATE_USER = '''
CREATE USER "%(db_user)s";
'''

SQL_CREATE_DB = '''
CREATE DATABASE "%(db_name)s" WITH OWNER "%(db_owner)s";
'''

SQL_INIT_GRANT_DB = '''
GRANT ALL ON DATABASE "%(db_name)s" TO "%(db_owner)s";
REVOKE ALL ON DATABASE "%(db_name)s" FROM PUBLIC;
'''

SQL_REVOKE_DB = '''
REVOKE ALL ON DATABASE "%(db_name)s" FROM "%(db_user)s";
'''

SQL_GRANT_DB = '''
GRANT %(db_grants)s ON DATABASE "%(db_name)s" TO "%(db_user)s";
'''

SQL_DESC_COLUMN = '"%(col_name)s" %(col_type)s'
SQL_PK = 'PRIMARY KEY %(pk_cols)s'
SQL_FK = 'FOREIGN KEY %(local_columns)s REFERENCES "%(remote_table)s" %(remote_columns)s'
SQL_CREATE_TABLE = '''
CREATE TABLE "%(table_name)s" (%(columns_sql)s);
'''

SQL_DROP_TABLE = '''DROP TABLE "%(table_name)s"'''

SQL_ESTIMATE_ROWS_COUNT = '''
SELECT reltuples::BIGINT AS estimate FROM pg_class WHERE relname='%(table_name)s';
'''

DEFAULT_CONNECT_TIMEOUT = 4     # seconds

def identifier_list_to_sql(l):
    return "(" + ', '.join('"%s"' % name for name in l) + ")"

class PostgreSQLServerCursor(psycopg2.extensions.cursor):
    def close(self):
        psycopg2.extensions.cursor.close(self)
        # server-side cursors, even closed, may still lock
        # the tables that were fetched. committing ensures
        # tables are no longer locked.
        self.connection.commit()
        if DEBUG_CURSORS:
            print('cursor ' + self.name + ' released')
    def __del__(self):
        # ensures cursor is closed when deleting
        if not self.closed:
            self.close()
        # let's ensure possible evolutions of psycopg2 will
        # not break this.
        if hasattr(psycopg2.extensions.cursor, '__del__'):
            psycopg2.extensions.cursor.__del__(self)

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
        if DEBUG_CURSORS:
            print("opening server cursor", cursor_name)
        cursor = db_conn.cursor(name = cursor_name,
                                cursor_factory=PostgreSQLServerCursor)
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
    def collect_grants(admin_db_conn, metadata_collector):
        with admin_db_conn.cursor() as cursor:
            cursor.execute(SQL_GET_DS_GRANTS)
            for row in cursor:
                grant = GRANT_LEVELS.write if row['usecreatedb'] else GRANT_LEVELS.read
                metadata_collector.register_datastore_grant(row['usename'], grant)
    @staticmethod
    def collect_databases(admin_db_conn, metadata_collector):
        with admin_db_conn.cursor() as cursor:
            cursor.execute(SQL_GET_DBS)
            for row in cursor:
                dbname = row[0]
                if dbname not in IGNORED_DATABASES:
                    metadata_collector.register_database(dbname)
    @staticmethod
    def collect_database_grants(admin_db_conn, metadata_collector):
        # we must tell metadata_visitor which user has READ, WRITE, OWNER
        # access to which database
        with admin_db_conn.cursor() as cursor:
            cursor.execute(SQL_GET_DB_ACCESS_GRANTS)
            for dbuser, dbname, privtype in cursor:
                # convert to sakura access grants
                grant = {   'CONNECT':  GRANT_LEVELS.read,
                            'CREATE':   GRANT_LEVELS.write,
                            'OWNER':    GRANT_LEVELS.own
                }[privtype]
                if dbname not in IGNORED_DATABASES:
                    metadata_collector.register_database_grant(dbuser, dbname, grant)
    @staticmethod
    def collect_database_tables(db_conn, metadata_collector):
        # db_conn must be connected to the targeted database
        with db_conn.cursor() as cursor:
            cursor.execute(SQL_GET_DB_TABLES)
            for row in cursor:
                tablename = row[0]
                metadata_collector.register_table(tablename)
    @staticmethod
    def collect_table_primary_key(db_conn, metadata_collector, table_name):
        with db_conn.cursor() as cursor:
            cursor.execute(SQL_GET_TABLE_PRIMARY_KEY % dict(table_name = table_name))
            for row in cursor:
                pk_col_names = row[0]
                metadata_collector.register_primary_key(table_name, pk_col_names)
    @staticmethod
    def collect_table_foreign_keys(db_conn, metadata_collector, table_name):
        with db_conn.cursor() as cursor:
            cursor.execute(SQL_GET_TABLE_FOREIGN_KEYS % dict(table_name = table_name))
            for row in cursor:
                pk_col_names = row[0]
                metadata_collector.register_foreign_key(
                        table_name,
                        local_columns = row['attnames'],
                        remote_table = row['fk_table'],
                        remote_columns = row['fk_attnames'])
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
    @staticmethod
    def collect_table_count_estimate(db_conn, metadata_collector, table_name):
        sql = SQL_ESTIMATE_ROWS_COUNT % dict(table_name = table_name)
        with db_conn.cursor() as cursor:
            cursor.execute(sql)
            count_estimate = cursor.fetchone()[0]
            metadata_collector.register_count_estimate(
                    table_name,
                    count_estimate)
    @staticmethod
    def create_user(admin_db_conn, db_user):
        with admin_db_conn.cursor() as cursor:
            cursor.execute(SQL_CREATE_USER % dict(db_user = db_user))
    @staticmethod
    def create_db(admin_db_conn, db_name, db_owner):
        # CREATE DATABASE requires to set autocommit, and
        # cannot be execute in a multiple-statements string
        saved_mode = admin_db_conn.autocommit
        admin_db_conn.commit() # complete running transaction if any
        admin_db_conn.autocommit = True
        with admin_db_conn.cursor() as cursor:
            for sql in (SQL_CREATE_DB, SQL_INIT_GRANT_DB):
                cursor.execute(sql % dict(
                        db_name = db_name,
                        db_owner = db_owner))
        admin_db_conn.autocommit = saved_mode
    @staticmethod
    def create_table(db_conn, table_name, columns, primary_key, foreign_keys):
        columns_sql = []
        for col_name, col_type in columns:
            col_sql = SQL_DESC_COLUMN % dict(
                col_name = col_name,
                col_type = TYPES_SAKURA_TO_PG[col_type]
            )
            columns_sql.append(col_sql)
        if len(primary_key) > 0:
            constraint_sql = SQL_PK % dict(
                pk_cols = identifier_list_to_sql(primary_key))
            columns_sql.append(constraint_sql)
        for fk_info in foreign_keys:
            constraint_sql = SQL_FK % dict(
                local_columns = identifier_list_to_sql(fk_info['local_columns']),
                remote_table = fk_info['remote_table'],
                remote_columns = identifier_list_to_sql(fk_info['remote_columns'])
            )
            columns_sql.append(constraint_sql)
        sql = SQL_CREATE_TABLE % dict(
            table_name = table_name,
            columns_sql = ', '.join(columns_sql)
        )
        with db_conn.cursor() as cursor:
            cursor.execute(sql)
        db_conn.commit()
    @staticmethod
    def delete_table(db_conn, table_name):
        try:
            with db_conn.cursor() as cursor:
                cursor.execute(SQL_DROP_TABLE % dict(table_name = table_name))
            db_conn.commit()
        except psycopg2.Error as e:
            raise APIRequestError(e.pgerror)
    @staticmethod
    def add_rows(db_conn, table_name, value_wrappers, rows):
        try:
            if len(rows) == 0:
                return  # nothing to do
            tuple_pattern = '(' + ','.join(value_wrappers) + ')'
            with db_conn.cursor() as cursor:
                args_str = b','.join(cursor.mogrify(tuple_pattern, row) for row in rows)
                cursor.mogrify('"%s"' % table_name)
                cursor.execute(b"INSERT INTO " + cursor.mogrify('"%s"' % table_name) + \
                               b" VALUES " + args_str)
            db_conn.commit()
        except psycopg2.Error as e:
            raise APIRequestError(e.pgerror)
    @staticmethod
    def set_database_grant(admin_db_conn, db_name, db_user, grant):
        with admin_db_conn.cursor() as cursor:
            # start by removing existing grants for this user
            cursor.execute(SQL_REVOKE_DB % dict(
                    db_name = db_name,
                    db_user = db_user))
            # add needed grants
            if grant >= GRANT_LEVELS.read:
                db_grants = {
                    GRANT_LEVELS.read: 'CONNECT',
                    GRANT_LEVELS.write: 'CONNECT, CREATE, TEMPORARY'
                }[grant]
                cursor.execute(SQL_GRANT_DB % dict(
                        db_name = db_name,
                        db_user = db_user,
                        db_grants = db_grants))
        admin_db_conn.commit()
    @staticmethod
    def set_datastore_grant(admin_db_conn, ds_user, grant):
        with admin_db_conn.cursor() as cursor:
            ds_grants = {
                GRANT_LEVELS.hide:  'NOLOGIN NOCREATEDB',
                GRANT_LEVELS.list:  'NOLOGIN NOCREATEDB',
                GRANT_LEVELS.read:  'LOGIN   NOCREATEDB',
                GRANT_LEVELS.write: 'LOGIN   CREATEDB'
            }[grant]
            cursor.execute(SQL_SET_DS_GRANTS % dict(
                    ds_user = ds_user,
                    ds_grants = ds_grants))
        admin_db_conn.commit()

DRIVER = PostgreSQLDBDriver

