import sakura.hub.conf as conf
from sakura.common.sqlite import SQLiteDB

DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS Project (
    project_id SERIAL PRIMARY KEY,
    gui_data TEXT
);

CREATE TABLE IF NOT EXISTS Daemon (
    daemon_id SERIAL PRIMARY KEY,
    connected BOOLEAN
);

CREATE TABLE IF NOT EXISTS OpInstance (
    op_id SERIAL PRIMARY KEY,
    project_id REFERENCES Project(project_id),
    daemon_id REFERENCES Daemon(daemon_id)
);
"""

class CentralStorage(SQLiteDB):
    def __init__(self):
        # parent constructor
        SQLiteDB.__init__(self, conf.work_dir + '/central.db')
        # create the db schema
        self.executescript(DB_SCHEMA)
        self.commit()
