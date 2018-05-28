import re, time, io, csv, bottle
from sakura.hub.context import get_context

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
            columns = tuple(c.pack() for c in self.ordered_columns),
            primary_key = self.primary_key,
            foreign_keys = tuple(self.foreign_keys),
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
        return self.remote_instance.get_range(
                row_start,
                row_end
        )
    def add_rows(self, data):
        return self.remote_instance.add_rows(
                data
        )
    def update_attributes(self, **kwargs):
        if 'primary_key' in kwargs:
            self.primary_key = kwargs.pop('primary_key')
        if 'foreign_keys' in kwargs:
            self.foreign_keys = kwargs.pop('foreign_keys')
        # update metadata
        metadata = dict(self.metadata)
        metadata.update(**kwargs)
        self.metadata = metadata
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
                get_context().columns.restore_column(table, col_id, *col) \
                        for col_id, col in enumerate(columns))
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
        context = get_context()
        if creation_date is None:
            creation_date = time.time()
        # register in central db
        new_table = cls(database = database,
                        name = name)
        cols = []
        for col_id, col_info in enumerate(columns):
            col = context.columns.create_column(new_table, col_id, *col_info)
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
    def stream_csv(self, transfer):
        count_estimate = self.remote_instance.get_count_estimate()
        count_transfered = 0
        csv_file_name = re.sub(r'[^a-z0-9]', '-',
                                self.name.lower()) + '.csv'
        bottle.response.set_header('content-disposition',
                        'attachment; filename="%s"' % csv_file_name)
        # header line
        yield ','.join(c.col_name for c in self.columns)
        # data rows
        buf = io.StringIO()
        writer = csv.writer(buf)
        for chunk in self.remote_instance.stream.chunks():
            writer.writerows(chunk.tolist())
            yield buf.getvalue()
            buf.truncate(0)
            buf.seek(0)
            count_transfered += chunk.size
            transfer.notify_estimate(count_transfered, count_estimate)
        transfer.notify_done()
