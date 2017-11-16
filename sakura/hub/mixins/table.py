class TableMixin:
    def pack(self):
        return dict(
            table_id = self.id,
            database_id = self.database.id,
            name = self.name,
            short_desc = self.short_desc,
            creation_date = self.creation_date,
            columns = tuple(c.pack() for c in self.columns)
        )
    @classmethod
    def create_or_update(cls, database, db_table_name, **kwargs):
        table = cls.get(database = database, db_table_name = db_table_name)
        if table is None:
            # default for the human-readable name will be the name found
            # inside the database
            if 'name' not in kwargs:
                kwargs['name'] = db_table_name
            table = cls(database = database, db_table_name = db_table_name, **kwargs)
        else:
            table.set(**kwargs)
        return table
    @classmethod
    def restore_table(cls, context, database, columns, **tbl):
        table = cls.create_or_update(database, **tbl)
        table.columns = set(context.columns.restore_column(context, table, *col) for col in columns)
        return table

