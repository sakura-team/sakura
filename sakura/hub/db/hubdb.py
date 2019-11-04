import re, sys, types
from sakura.hub import conf
from sakura.hub.db.schema import define_schema
from pony.orm import Database as PonyDatabase,      \
                     commit as pony_commit,         \
                     sql_debug,                     \
                     db_session as pony_db_session, \
                     CommitException, sql_debug

DEBUG=0
#DEBUG=1

if DEBUG == 1:
    sql_debug(True)

def commit():
    real_exception = None
    try:
        pony_commit()
    except CommitException as e:
        # check if this is not a disguised KeyboardInterrupt
        if hasattr(e, 'exceptions') and \
                e.exceptions[0][0] == KeyboardInterrupt:
            real_exception = KeyboardInterrupt
        else:
            real_exception = e
    if real_exception is not None:
        raise real_exception

# Since we use gevent's greenlets, we may get recursive sessions
# in the current thread.
# Default behavior of pony is to ignore nested sessions.
# With the following object, we ensure db updates are commited
# when we leave a nested session.

db_session = pony_db_session(optimistic = False)

class MyDBSession:
    ENV_DB_SESSION = None
    def __enter__(self):
        if MyDBSession.ENV_DB_SESSION is None:
            MyDBSession.ENV_DB_SESSION = db_session.__enter__()
        return MyDBSession.ENV_DB_SESSION
    def __exit__(self, type, value, traceback):
        commit()

def db_session_wrapper():
    return MyDBSession()

class CentralDB(PonyDatabase):
    def __init__(self, db_path):
        # parent constructor
        PonyDatabase.__init__(self)
        self.db_path = db_path
    def prepare(self):
        # init db, create tables if missing
        self.bind(provider='sqlite', filename=self.db_path, create_db=True)
        self.generate_mapping(create_tables=True)
    def session(self):
        return db_session
    def propose_sanitized_names(self, orig_name, prefix=''):
        # propose names containing only lowercase letters, numbers
        # or underscore, for internal use, by sanitizing <orig_name>
        base_db_name = prefix + re.sub('[^a-z0-9]+', '_', orig_name.lower())
        if re.match('^[^a-z]', base_db_name):
            base_db_name = '_' + base_db_name
        suffix_index = 0
        db_name = base_db_name
        while True:
            yield db_name
            db_name = base_db_name + '_' + str(suffix_index)
            suffix_index += 1

def instanciate_db():
    db = CentralDB(conf.work_dir + '/hub.db')
    define_schema(db)
    db.prepare()
    return db

