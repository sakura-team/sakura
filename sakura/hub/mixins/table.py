import time

class TableMixin:
    @property
    def remote_instance(self):
        return self.database.remote_instance.tables[self.name]
    @property
    def ordered_columns(self):
        return sorted(self.columns, key=lambda col: col.col_id)
    def pack(self):
        return dict(
            table_id = self.id,
            database_id = self.database.id,
            name = self.name,
            short_desc = self.short_desc,
            creation_date = self.creation_date,
            columns = tuple(c.pack() for c in self.ordered_columns),
            primary_key = self.primary_key,
            foreign_keys = tuple(self.foreign_keys)
        )
    def create_on_datastore(self, context):
        user = 'etienne'               # TODO: handle this properly
        password = 'sakura_etienne'    # TODO: handle this properly
        # adapt foreign keys because daemon need table names, not IDs
        fk = []
        for fk_info in self.foreign_keys:
            remote_table = context.tables[fk_info['remote_table_id']]
            fk.append(dict(
                local_columns = fk_info['local_columns'],
                remote_columns = fk_info['remote_columns'],
                remote_table = remote_table.name
            ))
        self.database.remote_instance.create_table(
                self.name,
                tuple(c.pack_for_daemon() for c in self.ordered_columns),
                self.primary_key,
                fk)
    def delete_table(self):
        # delete table on datastore
        self.database.remote_instance.delete_table(self.name)
        # delete instance in local db
        self.delete()
    def get_range(self, row_start, row_end):
        user = 'etienne'               # TODO: handle this properly
        password = 'sakura_etienne'    # TODO: handle this properly
        return self.remote_instance.get_range(
                row_start,
                row_end
        )
    def add_rows(self, data):
        user = 'etienne'               # TODO: handle this properly
        password = 'sakura_etienne'    # TODO: handle this properly
        return self.remote_instance.add_rows(
                data
        )
    @classmethod
    def create_or_update(cls, database, name, **kwargs):
        table = cls.get(database = database, name = name)
        if table is None:
            table = cls(database = database, name = name, **kwargs)
        else:
            table.set(**kwargs)
        return table
    @classmethod
    def restore_table(cls, context, database, columns, **tbl):
        table = cls.create_or_update(database, **tbl)
        table.columns = set(
                context.columns.restore_column(context, table, col_id, *col) \
                        for col_id, col in enumerate(columns))
        return table
    def update_foreign_keys(self, context, foreign_keys):
        self.foreign_keys = []
        for fk_info in foreign_keys:
            # daemon sends remote table name, we need its ID
            remote_table = context.tables.get(database = self.database,
                                                name = fk_info['remote_table'])
            self.foreign_keys.append(dict(
                local_columns = fk_info['local_columns'],
                remote_columns = fk_info['remote_columns'],
                remote_table_id = remote_table.id
            ))
    @classmethod
    def create_table(cls, context, database, name, columns,
                            creation_date = None, **kwargs):
        if creation_date is None:
            creation_date = time.time()
        # register in central db
        new_table = cls(database = database,
                        name = name,
                        creation_date = creation_date)
        cols = []
        for col_id, col_info in enumerate(columns):
            col = context.columns.create_column(context, new_table, col_id, *col_info)
            cols.append(col)
        new_table.set(columns = cols, **kwargs)
        # request daemon to create table on the remote datastore
        new_table.create_on_datastore(context)
        # return table_id
        context.db.commit()
        return new_table.id

