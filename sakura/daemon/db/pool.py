from time import time
import weakref
# This is the minimum time we keep connections alive when idle.
POOL_MIN_DELAY = 20.0   # seconds
DEBUG = False

class PooledConnection:
    def __init__(self, pool, conn):
        self.pool = pool
        self.conn = conn
        self.idle_start = None
    def close(self):
        self.pool.on_connection_close(self)
    def cursor(self, *args, **kwargs):
        return self.conn.cursor(*args, **kwargs)
    def __enter__(self):
        return self
    def __exit__(self, *args):
        self.close()
    @property
    def autocommit(self):
        return self.conn.autocommit
    @autocommit.setter
    def autocommit(self, val):
        self.conn.autocommit = val
    def commit(self):
        return self.conn.commit()
    def __del__(self):
        if DEBUG:
            print('******* closed connection')
        self.conn.close()

class ConnectionPool:
    instances = weakref.WeakSet()
    def __init__(self, connect_func):
        self.pooled_conns = set()
        self.free_conns = set()
        self.connect_func = connect_func
        ConnectionPool.instances.add(self)
    def connect(self):
        if len(self.free_conns) == 0:
            conn = self.connect_func()
            if DEBUG:
                print('******* NEW connection')
            conn = PooledConnection(self, conn)
        else:
            conn = self.free_conns.pop()
        self.pooled_conns.add(conn)
        return conn
    def on_connection_close(self, conn):
        if conn in self.pooled_conns:
            self.pooled_conns.discard(conn)
            self.free_conns.add(conn)
            conn.idle_start = time()
    def cleanup(self):
        cur_time = time()
        obsolete_conns = set(
                conn for conn in self.free_conns \
                if (conn.idle_start + POOL_MIN_DELAY) < cur_time)
        self.free_conns -= obsolete_conns
    @staticmethod
    def cleanup_all():
        for pool in ConnectionPool.instances:
            pool.cleanup()
    @staticmethod
    def plan_cleanup(planner):
        planner.plan(POOL_MIN_DELAY/2, ConnectionPool.cleanup_all)
