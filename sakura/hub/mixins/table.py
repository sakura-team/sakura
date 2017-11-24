import time
from sakura.common.tools import greenlet_env

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
            columns = tuple(c.pack() for c in self.ordered_columns)
        )
    def create_on_datastore(self):
        greenlet_env.user = 'etienne'               # TODO: handle this properly
        greenlet_env.password = 'sakura_etienne'    # TODO: handle this properly
        self.database.remote_instance.create_table(
                greenlet_env.user,
                greenlet_env.password,
                self.name,
                tuple(c.pack_for_daemon() for c in self.ordered_columns))
    def get_range(self, row_start, row_end):
        greenlet_env.user = 'etienne'               # TODO: handle this properly
        greenlet_env.password = 'sakura_etienne'    # TODO: handle this properly
        return self.remote_instance.get_range(
                greenlet_env.user,
                greenlet_env.password,
                row_start,
                row_end
        )
    def add_rows(self, data, date_formats):
        greenlet_env.user = 'etienne'               # TODO: handle this properly
        greenlet_env.password = 'sakura_etienne'    # TODO: handle this properly
        return self.remote_instance.add_rows(
                greenlet_env.user,
                greenlet_env.password,
                data,
                date_formats
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
        new_table.create_on_datastore()
        # return table_id
        context.db.commit()
        return new_table.id

