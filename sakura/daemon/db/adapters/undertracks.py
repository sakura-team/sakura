from sakura.common.io import pack
from sakura.common.tools import override_object

class UTTableOverride:
    def __init__(self, sakura_table_name):
        self.name = sakura_table_name

class UTExperimentAsDB:
    def __init__(self, ds, db_name, exp_name, owner, users):
        self.ds = ds
        self.exp_name = exp_name
        self.db_name = db_name
        self.owner = owner
        self.users = users
        self._tables = None
    @property
    def tables(self):
        if self._tables is None:
            self._tables = {}
            ut_tables = self.ds.databases['undertracks'].tables
            for suffix in ('logs', 'logsinfo', 'description', 'users', 'context', 'actions'):
                sakura_table_name = suffix.capitalize()
                ut_table_name = self.exp_name + suffix
                if ut_table_name in ut_tables:
                    ut_table = ut_tables[ut_table_name]
                    table = override_object(ut_table, UTTableOverride(sakura_table_name))
                    self._tables[sakura_table_name] = table
        return self._tables
    def pack(self):
        return pack(dict(
            name = self.db_name,
            owner = self.owner,
            tables = self.tables.values(),
            users = self.users
        ))
    def overview(self):
        return dict(
            name = self.db_name,
            owner = self.owner,
            users = self.users
        )

class UTDatastoreOverride:
    def __init__(self, engine, ds):
        self.engine = engine
        self.ds = ds
        self.known_emails = {}
        self._databases = None
    def parse_viewers(self, s):
        if s is None or s == '':
            return {}
        users = []
        for email in s.strip('_!!_').split('_!!_'):
            login = self.get_login_from_email(email.strip())
            if login is not None:
                users.append(login)
        return { user: dict(READ=True, WRITE=False) for user in users }
    def get_login_from_email(self, email):
        if email not in self.known_emails:
            self.known_emails[email] = \
                    self.engine.hub.get_login_from_email(email)
        return self.known_emails[email]
    def ut_experiments(self):
        metadata_tb = self.ds.databases['undertracks'].tables['metadata']
        for exp_name, owner_email, viewers in metadata_tb.stream.select_columns(0, 3, 6):
            owner_login = self.get_login_from_email(owner_email)
            users = self.parse_viewers(viewers)
            yield 'UT - ' + exp_name, exp_name, owner_login, users
    @property
    def databases(self):
        if self._databases is None:
            self._databases = {
                db_name: UTExperimentAsDB(self.ds, db_name, exp_name, owner, users) \
                    for db_name, exp_name, owner, users in self.ut_experiments()
            }
        return self._databases

class UTDatastoreAdapter:
    NAME = 'undertracks'
    @staticmethod
    def adapt(engine, ds):
        return override_object(ds, UTDatastoreOverride(engine, ds))

ADAPTER = UTDatastoreAdapter

