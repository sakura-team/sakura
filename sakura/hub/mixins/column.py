class ColumnMixin:
    def pack(self):
        # TODO: we should not expose daemon tags here, they
        # should only be used for the processing on the daemon side.
        # on the daemon side, the abstract type (e.g. timestamp, etc.)
        # should be returned when probing, instead of native db type + tags.
        tags = tuple(set(self.daemon_tags) | set(self.user_tags)) # union
        return self.col_name, self.col_type, tags
    def pack_for_daemon(self):
        return self.db_col_name, self.col_type
    @classmethod
    def create_or_update(cls, table, db_col_name, **kwargs):
        column = cls.get(table = table, db_col_name = db_col_name)
        if column is None:
            if 'col_name' not in kwargs:
                kwargs['col_name'] = db_col_name
            column = cls(table = table, db_col_name = db_col_name, **kwargs)
        else:
            column.set(**kwargs)
        return column
    @classmethod
    def restore_column(cls, context, table, db_col_name, col_type, daemon_tags):
        return cls.create_or_update(table, db_col_name,
                                    col_type = col_type,
                                    daemon_tags = daemon_tags)
    @classmethod
    def generate_db_col_name(cls, context, table, col_name):
        # compute a sanitized name not used already
        for db_col_name in context.db.propose_sanitized_names(col_name):
            if context.columns.get(
                            table = table,
                            db_col_name = db_col_name) is None:
                return db_col_name  # OK db_col_name is free
    @classmethod
    def create_column(cls, context, table, col_name, col_type, user_tags):
        db_col_name = cls.generate_db_col_name(context, table, col_name)
        return cls.create_or_update(table, db_col_name,
                                    col_name = col_name,
                                    col_type = col_type,
                                    user_tags = user_tags)
