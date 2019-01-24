import time
from sakura.common.io import pack
from sakura.common.tools import override_object
from sakura.common.access import GRANT_LEVELS, ACCESS_SCOPES

class UTTableOverride:
    def __init__(self, sakura_table_name):
        self.name = sakura_table_name

METADATA_TRANSLATION = dict(
    studydescription = 'short_desc',
    studyagenttype = 'agent_type',
    studytopic = 'topic'
)

class UTExperimentAsDB:
    def __init__(self, ds, exp_name, grants):
        self.ds = ds
        self.exp_name = exp_name
        self.db_name = 'UT - ' + exp_name
        self.grants = grants
        self._tables = None
        self.metadata = {}
        self.init_description_attrs()
    def init_description_attrs(self):
        description_tb_name = self.exp_name + 'description'
        if description_tb_name not in self.ds.databases['undertracks'].tables:
            return
        description_tb = self.ds.databases['undertracks'].tables[description_tb_name]
        description_row = tuple(description_tb.source())[0]
        #print("** " + self.exp_name)
        #print(tuple((c.col_name, description_row[idx]) for idx, c in enumerate(description_tb.columns)))
        for idx, c in enumerate(description_tb.columns):
            val = description_row[idx]
            if c.col_name == 'studyname':
                self.db_name = 'UT - ' + val
            elif c.col_name in METADATA_TRANSLATION:
                field_name = METADATA_TRANSLATION[c.col_name]
                self.metadata[field_name] = val
            elif c.col_name == 'studyispublic':
                self.metadata['access_scope'] = ACCESS_SCOPES.public if val == 'on' else ACCESS_SCOPES.private
            elif c.col_name == 'studybeginingdate':
                self.metadata['creation_date'] = int(time.mktime(time.strptime(val, '%d/%m/%Y')))
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
            tables = self.tables.values(),
            grants = self.grants,
            **self.metadata
        ))
    def overview(self):
        return dict(
            name = self.db_name,
            grants = self.grants,
            **self.metadata
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
        return { user: GRANT_LEVELS.read for user in users }
    def get_login_from_email(self, email):
        if email not in self.known_emails:
            self.known_emails[email] = \
                    self.engine.hub.get_login_from_email(email)
        return self.known_emails[email]
    def ut_experiments(self):
        metadata_tb = self.ds.databases['undertracks'].tables['metadata']
        for exp_name, owner_email, viewers in metadata_tb.source().select_columns(0, 3, 6):
            grants = self.parse_viewers(viewers)
            owner_login = self.get_login_from_email(owner_email)
            if owner_login is not None:
                grants[owner_login] = GRANT_LEVELS.own
            yield exp_name, grants
    @property
    def databases(self):
        if self._databases is None:
            self._databases = {}
            for exp_name, grants in self.ut_experiments():
                db = UTExperimentAsDB(self.ds, exp_name, grants)
                self._databases[db.db_name] = db
        return self._databases

class UTDatastoreAdapter:
    NAME = 'undertracks'
    @staticmethod
    def adapt(engine, ds):
        return override_object(ds, UTDatastoreOverride(engine, ds))

ADAPTER = UTDatastoreAdapter

