import time
from sakura.common.tools import greenlet_env

class DatabaseMixin:
    @property
    def online(self):
        return self.datastore.online and self.datastore.daemon.connected
    @property
    def remote_instance(self):
        return self.datastore.remote_instance.databases[self.name]
    def pack(self):
        return dict(
            tags = self.tags,
            contacts = tuple(u.login for u in self.contacts),
            database_id = self.id,
            datastore_id = self.datastore.id,
            name = self.name,
            short_desc = self.short_desc,
            creation_date = self.creation_date,
            owner = None if self.owner is None else self.owner.login,
            users_rw = tuple(u.login for u in self.users_rw),
            users_ro = tuple(u.login for u in self.users_ro),
            online = self.online
        )
    def get_full_info(self, context):
        # start with general metadata
        result = self.pack()
        # if online, explore tables
        if self.online:
            self.update_tables(context)
            result['tables'] = tuple(t.pack() for t in self.tables)
        return result
    def update_tables(self, context):
        # ask daemon
        info_from_daemon = self.remote_instance.pack()
        self.tables = set(
            context.tables.restore_table(context, self, **tbl) \
                    for tbl in info_from_daemon['tables']
        )
    def update_metadata(self, context, **kwargs):
        kwargs = self.format_metadata(context, **kwargs)
        # update database fields
        self.set(**kwargs)
    def create_on_datastore(self):
        self.datastore.remote_instance.create_db(
                self.name,
                self.owner.login)
    @classmethod
    def format_metadata(cls, context, users = None, contacts = None, **kwargs):
        # format users
        if users is not None:
            kwargs['users_rw'] = context.users.from_logins(
                        u for u, rights in users.items() if rights['WRITE'])
            kwargs['users_ro'] = context.users.from_logins(
                        u for u, rights in users.items() if rights['READ'])
        # format contacts
        if contacts is not None:
            kwargs['contacts'] = context.users.from_logins(contacts)
        return kwargs
    @classmethod
    def create_or_update(cls, context, datastore, name, **kwargs):
        kwargs = cls.format_metadata(context, **kwargs)
        database = cls.get(datastore = datastore, name = name)
        if database is None:
            database = cls(datastore = datastore, name = name, **kwargs)
        else:
            database.set(**kwargs)
        return database
    @classmethod
    def restore_database(cls, context, datastore, **db):
        return cls.create_or_update(context, datastore, **db)
    @classmethod
    def create_db(cls, context, datastore, name, creation_date = None, **kwargs):
        greenlet_env.user = 'etienne'    # TODO: handle this properly
        owner = greenlet_env.user
        if creation_date is None:
            creation_date = time.time()
        # register in central db
        new_db = cls(   datastore = datastore,
                        name = name,
                        owner = owner,
                        creation_date = creation_date)
        new_db.update_metadata(context, **kwargs)
        # request daemon to create db on the remote datastore
        new_db.create_on_datastore()
        # return database_id
        context.db.commit()
        return new_db.id

