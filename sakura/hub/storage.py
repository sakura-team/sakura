import sakura.hub.conf as conf
from sakura.common.sqlite import SQLiteDB

DB_SCHEMA = """
pragma foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Project (
    project_id INTEGER PRIMARY KEY AUTOINCREMENT,
    gui_data TEXT
);

CREATE TABLE IF NOT EXISTS Daemon (
    daemon_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS OpClass (
    cls_id INTEGER PRIMARY KEY AUTOINCREMENT,
    daemon_id INTEGER REFERENCES Daemon(daemon_id),
    name TEXT,
    UNIQUE(daemon_id, name)
);

CREATE TABLE IF NOT EXISTS OpInstance (
    op_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER REFERENCES Project(project_id),
    cls_id INTEGER REFERENCES OpClass(cls_id) ON DELETE CASCADE,
    gui_data TEXT
);

CREATE TABLE IF NOT EXISTS Link (
    link_id INTEGER PRIMARY KEY AUTOINCREMENT,
    src_op_id INTEGER REFERENCES OpInstance(op_id) ON DELETE CASCADE,
    src_out_id INTEGER,
    dst_op_id INTEGER REFERENCES OpInstance(op_id) ON DELETE CASCADE,
    dst_in_id INTEGER,
    gui_data TEXT
);

CREATE TABLE IF NOT EXISTS OpParam (
    op_id INTEGER REFERENCES OpInstance(op_id) ON DELETE CASCADE,
    param_id INTEGER,
    json_value TEXT,
    UNIQUE(op_id, param_id)
);

CREATE TABLE IF NOT EXISTS DataStore (
    datastore_id INTEGER PRIMARY KEY AUTOINCREMENT,
    daemon_id INTEGER REFERENCES Daemon(daemon_id),
    online BOOLEAN,
    host TEXT,
    driver TEXT
);

CREATE TABLE IF NOT EXISTS Database (
    database_id INTEGER PRIMARY KEY AUTOINCREMENT,
    datastore_id INTEGER REFERENCES DataStore(datastore_id) ON DELETE CASCADE,
    name TEXT,
    db_name TEXT,
    short_desc TEXT,
    created TIMESTAMP WITH TIME ZONE
);
"""

class CentralStorage(SQLiteDB):
    def __init__(self):
        # parent constructor
        SQLiteDB.__init__(self, conf.work_dir + '/central.db')
        # create the db schema
        self.executescript(DB_SCHEMA)
        self.commit()
