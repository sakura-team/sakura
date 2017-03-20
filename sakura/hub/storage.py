import sakura.hub.conf as conf
from sakura.common.sqlite import SQLiteDB

DB_SCHEMA = """
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
    cls_id INTEGER REFERENCES OpClass(cls_id)
);
"""

class CentralStorage(SQLiteDB):
    def __init__(self):
        # parent constructor
        SQLiteDB.__init__(self, conf.work_dir + '/central.db')
        # create the db schema
        self.executescript(DB_SCHEMA)
        self.commit()
