import time
from sakura.common.tools import greenlet_env
from enum import Enum
DB_RIGHTS = Enum('DB_RIGHTS', 'public restricted private')

class DatabaseMixin:
    @property
    def online(self):
        return self.datastore.online and self.datastore.daemon.connected
    @property
    def remote_instance(self):
        return self.datastore.remote_instance.databases[self.name]
    def pack(self):
        result = dict(
            tags = self.tags,
            contacts = tuple(u.login for u in self.contacts),
            database_id = self.id,
            datastore_id = self.datastore.id,
            name = self.name,
            creation_date = self.creation_date,
            rights = DB_RIGHTS(self.rights).name,
            owner = None if self.owner is None else self.owner.login,
            users_rw = tuple(u.login for u in self.users_rw),
            users_ro = tuple(u.login for u in self.users_ro),
            online = self.online
        )
        result.update(**self.metadata)
        return result
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
        # update tables (except foreign keys - a referenced table
        # may not be created yet otherwise)
        self.tables = set(
            context.tables.restore_table(context, self, **tbl_info) \
                    for tbl_info in info_from_daemon['tables']
        )
        # update foreign keys
        for tbl_info in info_from_daemon['tables']:
            table = context.tables.get(
                database = self,
                name = tbl_info['name']
            )
            table.update_foreign_keys(context, tbl_info['columns'])
    def update_metadata(self, context, **kwargs):
        kwargs = self.format_metadata(context, **kwargs)
        # update database fields
        self.set(**kwargs)
    def create_on_datastore(self):
        self.datastore.remote_instance.create_db(
                self.name,
                self.owner.login)
    @classmethod
    def format_metadata(cls, context, users = None, contacts = None, **metadata):
        args = dict(metadata = metadata)
        # format users
        if users is not None:
            args['users_rw'] = context.users.from_logins(
                        u for u, rights in users.items() if rights['WRITE'])
            args['users_ro'] = context.users.from_logins(
                        u for u, rights in users.items() if rights['READ'])
        # format contacts
        if contacts is not None:
            args['contacts'] = context.users.from_logins(contacts)
        return args
    @classmethod
    def create_or_update(cls, context, datastore, name, **kwargs):
        kwargs = cls.format_metadata(context, **kwargs)
        database = cls.get(datastore = datastore, name = name)
        if database is None:
            # if rights not specified (unknown database detected on a daemon),
            # default to private
            rights = kwargs.get('rights', DB_RIGHTS.private.value)
            database = cls(datastore = datastore, name = name, rights = rights, **kwargs)
        else:
            database.set(**kwargs)
        return database
    @classmethod
    def restore_database(cls, context, datastore, **db):
        return cls.create_or_update(context, datastore, **db)
    @classmethod
    def create_db(cls, context, datastore, name, rights, creation_date = None, **kwargs):
        greenlet_env.user = 'etienne'    # TODO: handle this properly
        owner = greenlet_env.user
        if creation_date is None:
            creation_date = time.time()
        # register in central db
        new_db = cls(   datastore = datastore,
                        name = name,
                        owner = owner,
                        rights = getattr(DB_RIGHTS, rights).value,
                        creation_date = creation_date)
        new_db.update_metadata(context, **kwargs)
        # request daemon to create db on the remote datastore
        new_db.create_on_datastore()
        # return database_id
        context.db.commit()
        return new_db.id

