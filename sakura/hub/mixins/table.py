import time
from sakura.hub.context import get_context
from sakura.common.access import GRANT_LEVELS
from sakura.hub.mixins.bases import BaseMixin

class TableMixin(BaseMixin):
    @property
    def grants(self):
        return self.database.grants
    @property
    def access_scope(self):
        return self.database.access_scope
    @property
    def readable(self):
        return self.database.readable
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
            columns = tuple(c.pack() for c in self.ordered_columns),
            primary_key = self.primary_key,
            foreign_keys = tuple(self.foreign_keys),
            dtype = self.get_dtype(),
            **self.metadata
        )
    def create_on_datastore(self):
        context = get_context()
        # adapt foreign keys because daemon need table names, not IDs
        fk = []
        for fk_info in self.foreign_keys:
            remote_table = context.tables[fk_info['remote_table_id']]
            fk.append(dict(
                local_columns = fk_info['local_columns'],
                remote_columns = fk_info['remote_columns'],
                remote_table = remote_table.name
            ))
        # create table on daemon
        self.database.remote_instance.create_table(
                self.name,
                tuple(c.pack_for_daemon() for c in self.ordered_columns),
                self.primary_key,
                fk)
        # let daemon know about user-defined tags
        tbl_col_tags = self.describe_col_tags()
        if max(map(len, tbl_col_tags)) > 0:
            self.remote_instance.set_col_tags(tbl_col_tags)
    def delete_table(self):
        self.database.assert_grant_level(GRANT_LEVELS.write,
                    'You are not delete a table of this database.')
        # delete table on datastore
        self.database.remote_instance.delete_table(self.name)
        # delete instance in local db
        self.delete()
    def get_range(self, row_start, row_end):
        return self.remote_instance.get_range(
                row_start,
                row_end
        )
    def chunks(self, allow_approximate=False):
        yield from self.remote_instance.chunks(allow_approximate=allow_approximate)
    def get_dtype(self):
        return self.remote_instance.get_dtype()
    def add_rows(self, data):
        self.database.assert_grant_level(GRANT_LEVELS.write,
                    'You are not allowed to write data to this database.')
        return self.remote_instance.add_rows(
                data
        )
    @classmethod
    def create_or_update(cls, database, name, **kwargs):
        table = cls.get(database = database, name = name)
        if table is None:
            table = cls(database = database, name = name)
        table.update_attributes(**kwargs)
        return table
    @classmethod
    def restore_table(cls, database, columns, **tbl):
        table = cls.create_or_update(database, **tbl)
        table.columns = set(
                get_context().columns.restore_column(table, *col) \
                        for col in columns)
        return table
    def update_foreign_keys(self, foreign_keys):
        self.foreign_keys = []
        for fk_info in foreign_keys:
            # daemon sends remote table name, we need its ID
            remote_table = get_context().tables.get(database = self.database,
                                                name = fk_info['remote_table'])
            self.foreign_keys.append(dict(
                local_columns = fk_info['local_columns'],
                remote_columns = fk_info['remote_columns'],
                remote_table_id = remote_table.id
            ))
    @classmethod
    def create_table(cls, database, name, columns,
                            creation_date = None, **kwargs):
        database.assert_grant_level(GRANT_LEVELS.write,
                        'You are not allowed to create tables on this database.')
        context = get_context()
        if creation_date is None:
            creation_date = time.time()
        # register in central db
        new_table = cls(database = database,
                        name = name)
        cols = []
        for col_info in columns:
            col = context.columns.create_column(new_table, *col_info)
            cols.append(col)
        new_table.columns = cols
        new_table.update_attributes(creation_date = creation_date,
                                    **kwargs)
        context.db.commit()
        table_id = new_table.id
        # request daemon to create table on the remote datastore
        new_table.create_on_datastore()
        # return table_id
        return table_id
    def stream_csv(self, transfer, gzip_compression=False):
        self.database.assert_grant_level(GRANT_LEVELS.read,
                    'You are not allowed to read data from this database.')
        rows_estimate = self.remote_instance.get_count_estimate()
        csv_stream = self.remote_instance.stream_csv(gzip_compression)
        for rows_transfered, bytes_transfered, s in csv_stream:
            transfer.notify_status(rows_transfered, rows_estimate, bytes_transfered)
            yield s
        transfer.notify_done()
    def describe_col_tags(self):
        tbl_col_tags = []
        for col in self.ordered_columns:
            tbl_col_tags.append(col.user_tags)
        return tbl_col_tags
