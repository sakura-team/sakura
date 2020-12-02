import psycopg2, re, uuid, numpy as np, greenlet
from gevent.socket import wait_read, wait_write
from collections import defaultdict
from psycopg2.extras import DictCursor
from psycopg2.extensions import POLL_OK, POLL_READ, POLL_WRITE, set_wait_callback, connection
from sakura.common.errors import APIRequestError
from sakura.common.access import GRANT_LEVELS
from sakura.daemon.db import CURSOR_MODE

DEBUG=False

# when in 'interactive' mode, we will tell the postgresql
# engine that it should optimize the server cursor query
# for quicky retrieval of this aproximate number of rows.
OPTIMISER_FETCH_SIZE = 2000

# psycopg should let gevent switch to other greenlets
def wait_callback(conn, timeout=None):
    while True:
        state = conn.poll()
        if state == POLL_OK:
            break
        try:
            if state == POLL_READ:
                wait_read(conn.fileno(), timeout=timeout)
            elif state == POLL_WRITE:
                wait_write(conn.fileno(), timeout=timeout)
            else:
                raise psycopg2.OperationalError("Bad result from poll: %r" % state)
        except greenlet.GreenletExit:
            # if greenlet is interrupted, cancel the db connection
            try:
                conn.cancel()
            except:
                pass
            raise

set_wait_callback(wait_callback)

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

TYPES_SAKURA_TO_PG_INPUT = {
    'int8':     'smallint',
    'int16':    'smallint',
    'int32':    'integer',
    'int64':    'bigint',
    'float32':  'real',
    'float64':  'double precision',
    'string':   'text',
    'bool':     'boolean',
    'date':     'double precision'
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

def esc(name):
    """ function to escape object names (database, table, column names) """
    return '"' + name.replace('%', '%%') + '"'

def register_column(metadata_collector, table_name, col_name, col_pgtype, col_meta, **params):
    select_clause_sql = esc(table_name) + "." + esc(col_name)
    where_clause_sql = select_clause_sql
    sort_clause_sql = select_clause_sql
    value_wrapper = '%s'
    tags = ()
    if col_pgtype.endswith('[]') or col_pgtype in ('hstore', 'json', 'jsonb'):
        col_type = 'opaque'
    elif col_pgtype in ('timestamp with time zone', 'timestamp without time zone', 'date'):
        col_type = 'date'
        select_clause_sql = 'extract(epoch from %(table_name)s.%(col_name)s) as %(col_name)s' % dict(
                                table_name = esc(table_name),
                                col_name = esc(col_name))
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
        select_clause_sql = 'ST_AsGeoJSON(%(table_name)s.%(col_name)s) as %(col_name)s' % dict(
                                table_name = esc(table_name),
                                col_name = esc(col_name))
        value_wrapper = 'ST_GeomFromGeoJSON(%s)'
        tags = ('geometry', 'supports_in')
    elif col_pgtype in ('longitude', 'latitude'):
        col_type = 'float64'
        parent_col_name = col_name[:-2]   # e.g. gps.X -> gps
        func_name = {'longitude': 'ST_X', 'latitude': 'ST_Y'}[col_pgtype]
        unaliased_sql = '%(func_name)s(%(table_name)s.%(parent_col_name)s)' % dict(
                                func_name = func_name,
                                table_name = esc(table_name),
                                parent_col_name = esc(parent_col_name),
                                col_name = esc(col_name))
        select_clause_sql = unaliased_sql + ' as ' + esc(col_name)
        sort_clause_sql = unaliased_sql
        tags = (col_pgtype,)    # 'latitude' or 'longitude'
    elif col_pgtype in TYPES_PG_TO_SAKURA.keys():
        col_type = TYPES_PG_TO_SAKURA[col_pgtype]
    else:
        raise RuntimeError('Unknown postgresql type: %s' % col_pgtype)
    return metadata_collector.register_column(
            table_name, col_name, col_type,
            select_clause_sql, where_clause_sql, sort_clause_sql, value_wrapper,
            tags, **params)

SQL_GET_DS_GRANTS = '''\
SELECT  usename, usecreatedb FROM pg_user;
'''

SQL_SET_DS_GRANTS = '''\
ALTER ROLE %(ds_user)s WITH %(ds_grants)s;
'''

SQL_GET_DS_USERS = '''\
SELECT rolname FROM pg_roles;
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
    WHERE  a.attrelid = '%(table_name)s'::regclass::oid
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
        WHERE   r.conrelid = '%(table_name)s'::regclass
          AND   r.contype = 'f'
          AND   r.confrelid = fk_table.oid)
    SELECT  json_agg(a.attname) as attnames,
            json_agg(fk_a.attname) as fk_attnames,
            fk.fk_table
    FROM    pg_attribute a, pg_attribute fk_a, fk_info fk
    WHERE   a.attrelid = '%(table_name)s'::regclass
      AND   a.attnum = fk.attnum
      AND   fk_a.attrelid = fk.fk_table_oid
      AND   fk_a.attnum = fk.fk_attnum
    GROUP BY fk.oid, fk.fk_table;
'''

SQL_GET_TABLE_PRIMARY_KEY = '''
    WITH pk_info AS (
        SELECT  unnest(indkey) as attnum
        FROM    pg_index
        WHERE   pg_index.indrelid = '%(table_name)s'::regclass::oid
        AND     indisprimary)
    SELECT  COALESCE(json_agg(a.attname), '[]') as attnames
    FROM pg_attribute a, pk_info pk
    WHERE a.attrelid = '%(table_name)s'::regclass
      AND a.attnum = pk.attnum;
'''

SQL_CREATE_USER = '''
CREATE USER %(db_user)s;
'''

SQL_CREATE_DB = '''
CREATE DATABASE %(db_name)s WITH OWNER %(db_owner)s;
'''

SQL_DROP_DB = '''
DROP DATABASE %(db_name)s;
'''

SQL_INIT_GRANT_DB = '''
GRANT ALL ON DATABASE %(db_name)s TO %(db_owner)s;
REVOKE ALL ON DATABASE %(db_name)s FROM PUBLIC;
'''

SQL_REVOKE_DB = '''
REVOKE ALL ON DATABASE %(db_name)s FROM %(db_user)s;
'''

SQL_GRANT_DB = '''
GRANT %(db_grants)s ON DATABASE %(db_name)s TO %(db_user)s;
'''

SQL_DESC_COLUMN = '%(col_name)s %(col_type)s'
SQL_PK = 'PRIMARY KEY %(pk_cols)s'
SQL_FK = 'FOREIGN KEY %(local_columns)s REFERENCES %(remote_table)s %(remote_columns)s'
SQL_CREATE_TABLE = '''
CREATE TABLE %(table_name)s (%(columns_sql)s);
'''

SQL_DROP_TABLE = '''DROP TABLE %(table_name)s'''

SQL_ESTIMATE_ROWS_COUNT = '''
select reltuples::BIGINT AS estimate FROM pg_class WHERE oid = '%(table_name)s'::regclass::oid;
'''

DEFAULT_CONNECT_TIMEOUT = 4     # seconds

def identifier_list_to_sql(l):
    return "(" + ', '.join(esc(name) for name in l) + ")"

class PostgreSQLCursor(DictCursor):
    def close(self):
        if self.closed:
            return
        super().close()
        if DEBUG and hasattr(self, 'name'):
            print('cursor ' + self.name + ' closed')

# let's consider this query:
# select * from t1, t2 where t1.a = t2.a order by t2.b
# (and we have indexes on t1.a, t2.a and t2.b)

# in many cases database engines generate this obvious query plan:
# join(t1.a,t2.a), then sort on t2.b

# the problem with this query plan, is that streaming output rows can
# only start at the end of the query plan execution (after the sort()).

# another possible query plan is the following:
# sort on t2.b, then
# for each output row r look for rows in t1 where t1.a = r.a,
# and output these joint rows.

# this query plan allows to start streaming rows very soon.
# but this query plan is not often selected because computing the whole
# resultset this way is slower than with the other query plan.

# some database systems propose a parameter allowing to skew the query
# engine towards quickly getting the first rows.
# this is the case of postgresql which proposes parameter 'cursor_tuple_fraction'.
# 'cursor_tuple_fraction' allows to indicate an estimation of the fraction of
# rows which will be fetched from a server cursor.

# the following connection subclass object makes use of this parameter
# to skew the database engine:
# - when profile is 'interactive', 'cursor_tuple_fraction' is set to a low
#   value: the database engine will try to generate query plans able to
#   quickly return first rows.
# - when profile is 'download', 'cursor_tuple_fraction' is set to 1.0

# in order to finely tune 'cursor_tuple_fraction' (when profile is 'interactive'),
# an estimation of expected total number of rows is first computed by running
# an EXPLAIN request.

class PostgreSQLConnection(connection):
    def cursor(self, cursor_mode = CURSOR_MODE.CLIENT,
                     profile = 'interactive',
                     profile_query = None,
                     **kwargs):
        if cursor_mode == CURSOR_MODE.CLIENT:
            # just use method of base class
            return super().cursor(cursor_factory = PostgreSQLCursor, **kwargs)
        elif cursor_mode == CURSOR_MODE.SERVER:
            if profile == 'interactive':
                if profile_query is None:
                    print("WARNING: unknown query when creating a cursor with 'interactive' profile.")
                    cursor_tuple_fraction = 0.1     # default value
                else:
                    # tell postgresql we will only retrieve a small number of rows
                    # from the cursor, by adjusting 'cursor_tuple_fraction' parameter
                    num_rows_estimate = PostgreSQLDBDriver.get_query_rows_count_estimate(
                                            self, *profile_query)
                    if num_rows_estimate <= OPTIMISER_FETCH_SIZE:
                        cursor_tuple_fraction = 1.0
                    else:
                        cursor_tuple_fraction = OPTIMISER_FETCH_SIZE / num_rows_estimate
            else:   # profile = download
                # tell postgresql we will retrieve all rows
                cursor_tuple_fraction = 1.0
            if DEBUG:
                print('cursor_tuple_fraction:', cursor_tuple_fraction)
            # set cursor_tuple_fraction
            with self.cursor() as cursor:
                cursor.execute('SET cursor_tuple_fraction TO %s', (cursor_tuple_fraction,))
            # create a server cursor for the real query
            cursor_name = str(uuid.uuid4()) # unique name
            if DEBUG:
                print("opening server cursor", cursor_name)
            cursor = self.cursor(name = cursor_name)
            # arraysize: default number of rows when using fetchmany()
            # itersize: default number of rows fetched from the backend
            #           at each network roundtrip (psycopg2-specific)
            cursor.arraysize = cursor.itersize
            return cursor

class PostgreSQLDBDriver:
    NAME = 'postgresql'
    @staticmethod
    def connect(**kwargs):
        # if database is not specified, connect to 'postgres' db
        if 'dbname' not in kwargs:
            kwargs['dbname'] = 'postgres'
        if 'connect_timeout' not in kwargs:
            kwargs['connect_timeout'] = DEFAULT_CONNECT_TIMEOUT
        kwargs['connection_factory'] = PostgreSQLConnection
        conn = psycopg2.connect(**kwargs)
        return conn
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
            cursor.execute(SQL_GET_TABLE_PRIMARY_KEY % dict(table_name = esc(table_name)), ())
            for row in cursor:
                pk_col_names = row[0]
                metadata_collector.register_primary_key(table_name, pk_col_names)
    @staticmethod
    def collect_table_foreign_keys(db_conn, metadata_collector, table_name):
        with db_conn.cursor() as cursor:
            cursor.execute(SQL_GET_TABLE_FOREIGN_KEYS % dict(table_name = esc(table_name)), ())
            for row in cursor:
                pk_col_names = row[0]
                metadata_collector.register_foreign_key(
                        table_name,
                        local_columns = row['attnames'],
                        remote_table = row['fk_table'],
                        remote_columns = row['fk_attnames'])
    @staticmethod
    def collect_table_columns(db_conn, metadata_collector, table_name):
        sql = SQL_GET_TABLE_COLUMNS % dict(table_name = esc(table_name))
        with db_conn.cursor() as cursor:
            cursor.execute(sql, ())
            rows = cursor.fetchall()
            for col_name, col_pgtype, col_comment in rows:
                col_meta = analyse_col_meta(col_comment)
                col_id = register_column(metadata_collector,
                    table_name, col_name, col_pgtype, col_meta)
                if col_pgtype.startswith('geometry(Point'):
                    register_column(metadata_collector,
                        table_name, col_name + '.X', 'longitude', {}, subcolumn_of=col_id)
                    register_column(metadata_collector,
                        table_name, col_name + '.Y', 'latitude', {}, subcolumn_of=col_id)
    @staticmethod
    def collect_table_count_estimate(db_conn, metadata_collector, table_name):
        sql = SQL_ESTIMATE_ROWS_COUNT % dict(table_name = esc(table_name))
        with db_conn.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            if len(rows) > 0:
                count_estimate = rows[0][0]
                metadata_collector.register_count_estimate(
                        table_name,
                        count_estimate)
    @staticmethod
    def get_query_rows_count_estimate(db_conn, sql_query, values):
        with db_conn.cursor() as cursor:
            cursor.execute('EXPLAIN ' + sql_query, values)
            first_line = cursor.fetchone()[0]
            rows_estimate = re.sub(r'.*rows=(\d+).*', r'\1', first_line)
            return int(rows_estimate)
    @staticmethod
    def has_user(admin_db_conn, db_user):
        with admin_db_conn.cursor() as cursor:
            cursor.execute(SQL_GET_DS_USERS)
            for row in cursor.fetchall():
                if row[0] == db_user:
                    return True
        return False
    @staticmethod
    def create_user(admin_db_conn, db_user):
        with admin_db_conn.cursor() as cursor:
            cursor.execute(SQL_CREATE_USER % dict(db_user = esc(db_user)), ())
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
                        db_name = esc(db_name),
                        db_owner = esc(db_owner)), ())
        admin_db_conn.autocommit = saved_mode
    @staticmethod
    def delete_db(admin_db_conn, db_name):
        # DROP DATABASE requires to set autocommit
        saved_mode = admin_db_conn.autocommit
        admin_db_conn.commit() # complete running transaction if any
        admin_db_conn.autocommit = True
        with admin_db_conn.cursor() as cursor:
            cursor.execute(SQL_DROP_DB % dict(db_name = esc(db_name)), ())
        admin_db_conn.autocommit = saved_mode
    @staticmethod
    def create_table(db_conn, table_name, columns, primary_key, foreign_keys):
        columns_sql = []
        for col_name, col_type in columns:
            col_sql = SQL_DESC_COLUMN % dict(
                col_name = esc(col_name),
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
                remote_table = esc(fk_info['remote_table']),
                remote_columns = identifier_list_to_sql(fk_info['remote_columns'])
            )
            columns_sql.append(constraint_sql)
        sql = SQL_CREATE_TABLE % dict(
            table_name = esc(table_name),
            columns_sql = ', '.join(columns_sql)
        )
        with db_conn.cursor() as cursor:
            cursor.execute(sql, ())
        db_conn.commit()
    @staticmethod
    def delete_table(db_conn, table_name):
        try:
            with db_conn.cursor() as cursor:
                cursor.execute(SQL_DROP_TABLE % dict(table_name = esc(table_name)), ())
            db_conn.commit()
        except psycopg2.Error as e:
            raise APIRequestError(e.pgerror)
    @staticmethod
    def add_rows(db_conn, table_name, columns, rows):
        try:
            if len(rows) == 0:
                return  # nothing to do
            num_cols = len(columns)
            col_names = tuple(esc(col.col_name) for col in columns)
            value_wrappers = tuple(col.value_wrapper for col in columns)
            pg_input_types = tuple(TYPES_SAKURA_TO_PG_INPUT[col.col_type] for col in columns)
            enumerated_cols = '(' + ', '.join(col_names) + ')'
            values_template = ','.join(['%s'] * len(rows))
            wrapped_cols = ', '.join(w % (n + "::" + t) for w, n, t in \
                            zip(value_wrappers, col_names, pg_input_types))
            query = \
            "WITH __temp_data" + enumerated_cols + " AS (VALUES " + values_template + ") " + \
            "INSERT INTO " + esc(table_name) + " " + \
            "SELECT " + wrapped_cols + " FROM __temp_data;"
            with db_conn.cursor() as cursor:
                cursor.execute(query, list(tuple(row) for row in rows))
            db_conn.commit()
        except psycopg2.Error as e:
            raise APIRequestError(e.pgerror)
    @staticmethod
    def set_database_grant(admin_db_conn, db_name, db_user, grant):
        with admin_db_conn.cursor() as cursor:
            # start by removing existing grants for this user
            cursor.execute(SQL_REVOKE_DB % dict(
                    db_name = esc(db_name),
                    db_user = esc(db_user)), ())
            # add needed grants
            if grant >= GRANT_LEVELS.read:
                db_grants = {
                    GRANT_LEVELS.read: 'CONNECT',
                    GRANT_LEVELS.write: 'CONNECT, CREATE, TEMPORARY'
                }[grant]
                cursor.execute(SQL_GRANT_DB % dict(
                        db_name = esc(db_name),
                        db_user = esc(db_user),
                        db_grants = db_grants), ())
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
                    ds_user = esc(ds_user),
                    ds_grants = ds_grants), ())
        admin_db_conn.commit()

DRIVER = PostgreSQLDBDriver

