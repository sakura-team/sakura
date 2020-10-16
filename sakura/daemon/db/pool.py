from time import time
import os, weakref
from sakura.common.release import auto_release
from sakura.daemon.db import CURSOR_MODE
# This is the minimum time we keep connections alive when idle.
POOL_MIN_DELAY = 20.0   # seconds
DEBUG = False

class PooledConnection:
    NEXT_ID = 0
    def __init__(self, driver, conn):
        self.conn_id = PooledConnection.NEXT_ID
        PooledConnection.NEXT_ID += 1
        self.driver = driver
        self.conn = conn
        self.idle_start = None
        self.current_cursor = None
        self.cursor_mode = CURSOR_MODE.CLIENT   # default value
    def set_cursor_mode(self, cursor_mode):
        self.cursor_mode = cursor_mode
    def cancel(self):
        if self.conn is not None:
            self.conn.cancel()
    def free_current_cursor(self):
        # cancel any previously running operation
        if self.current_cursor is not None and not self.current_cursor.closed:
            self.current_cursor.close()
    def execute(self, sql, *values):
        self.cursor().execute(sql, *values)
        return self.current_cursor
    def cursor(self):
        self.free_current_cursor()
        if self.cursor_mode == CURSOR_MODE.CLIENT:
            db_cursor = self.conn.cursor()
        elif self.cursor_mode == CURSOR_MODE.SERVER:
            db_cursor = self.driver.open_server_cursor(self.conn)
        self.current_cursor = db_cursor
        return self.current_cursor
    def __enter__(self):
        return self
    def __exit__(self, *args):
        self.close()
    @property
    def closed(self):
        return self.get_backend_id() is None
    @property
    def autocommit(self):
        return self.conn.autocommit
    @autocommit.setter
    def autocommit(self, val):
        self.conn.autocommit = val
    def commit(self):
        return self.conn.commit()
    def __str__(self):
        s = 'pooled_conn ' + str(self.conn_id)
        backend_id = self.get_backend_id()
        if backend_id is None:
            return s + ' <closed>'
        else:
            return s + (' (backend %d)' % backend_id)
    def get_id(self):
        return self.conn_id
    def get_backend_id(self):
        if self.conn is None or self.conn.closed:
            return None
        return self.conn.get_backend_pid()
    def release(self):
        if self.conn is not None:
            if DEBUG:
                print('******* releasing', self)
            try:
                self.free_current_cursor()
                self.conn.close()
                self.conn = None
            except:
                self.force_close()
    def force_close(self):
        if self.conn is not None:
            os.close(self.conn.fileno())
            self.conn = None
    def reset(self):
        self.free_current_cursor()

@auto_release
class Connection:
    def __init__(self, pool, pooled_connection):
        self.pool = pool
        self.pooled_connection = pooled_connection
        if DEBUG:
            self.print_verify = True
    def close(self):
        if self.pooled_connection is not None:
            if DEBUG:
                print('@@@@@@@@@@@@@@@@ CONNECTION', str(self), 'move to free')
            self.pool.move_to_free(self.pooled_connection)
            self.pooled_connection = None
    def __getattr__(self, attr):
        return getattr(self.pooled_connection, attr)
    def release(self):
        self.close()
    def __str__(self):
        if self.pooled_connection is None:
            return 'connection <empty>'
        else:
            return 'connection<' + str(self.pooled_connection) + '>'

@auto_release
class ConnectionPool:
    instances = weakref.WeakSet()
    def __init__(self, driver, connect_func):
        self.driver = driver
        self.pooled_conns = {}
        self.free_conns = {}
        self.connect_func = connect_func
        ConnectionPool.instances.add(self)
    def connect(self, cursor_mode=CURSOR_MODE.CLIENT, reuse_conn=None):
        if reuse_conn != None and not reuse_conn.closed:
            try:
                reuse_conn.reset()
                reuse_conn.set_cursor_mode(cursor_mode)
                return reuse_conn
            except:
                # this connection is blocked, delete it
                conn_id = reuse_conn.get_id()
                del self.pooled_conns[conn_id]
                reuse_conn.force_close()
                # open a new connection instead
                return self.connect(cursor_mode=cursor_mode)
        while True:
            if len(self.free_conns) == 0:
                conn = self.connect_func()
                conn = PooledConnection(self.driver, conn)
                conn_id = conn.get_id()
                if DEBUG:
                    print('******* NEW', conn)
                break
            else:
                # reuse a free connection (verifying it is still connected)
                conn_id, conn = self.free_conns.popitem()
                if not conn.closed:
                    break
        conn.set_cursor_mode(cursor_mode)
        self.pooled_conns[conn_id] = conn
        c = Connection(self, conn)
        if DEBUG:
            print('@@@@@@@@@@@@@@@@ connect() ->', c)
        return c
    def move_to_free(self, conn):
        conn_id = conn.get_id()
        # if conn.close() was called several times,
        # we might already have moved this to free_conns
        if conn_id in self.pooled_conns:
            self.free_conns[conn_id] = self.pooled_conns[conn_id]
            del self.pooled_conns[conn_id]
            conn.idle_start = time()
    def cleanup(self):
        cur_time = time()
        obsolete_conn_ids = set(
                conn_id for conn_id, conn in self.free_conns.items() \
                if (conn.idle_start + POOL_MIN_DELAY) < cur_time)
        for conn_id in obsolete_conn_ids:
            self.free_conns[conn_id].release()
            del self.free_conns[conn_id]
    def release(self):
        for conn in self.pooled_conns.values():
            conn.release()
        self.pooled_conns = {}
        for conn in self.free_conns.values():
            conn.release()
        self.free_conns = {}
    @staticmethod
    def cleanup_all():
        for pool in ConnectionPool.instances:
            pool.cleanup()
    @staticmethod
    def plan_cleanup(planner):
        planner.plan(POOL_MIN_DELAY/2, ConnectionPool.cleanup_all)
