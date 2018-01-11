class ColumnMixin:
    def pack(self):
        # TODO: we should not expose daemon tags here, they
        # should only be used for the processing on the daemon side.
        # on the daemon side, the abstract type (e.g. timestamp, etc.)
        # should be returned when probing, instead of native db type + tags.
        tags = tuple(set(self.daemon_tags) | set(self.user_tags)) # union
        return self.col_name, self.col_type, tags
    def pack_for_daemon(self):
        if self.foreign_key is None:
            fk_info = None
        else:
            fk_info = (self.foreign_key.table.name, self.foreign_key.col_name)
        return self.col_name, self.col_type, self.primary_key, fk_info
    @classmethod
    def create_or_update(cls, table, col_id, **kwargs):
        column = cls.get(table = table, col_id = col_id)
        if column is None:
            column = cls(table = table, col_id = col_id, **kwargs)
        else:
            column.set(**kwargs)
        return column
    @classmethod
    def restore_column(cls, context, table, col_id, col_name, col_type, daemon_tags, pk, fk_info):
        if fk_info is None:
            fk = None
        else:
            fk_table_name, fk_col_name = fk_info
            fk = context.columns.get(
                    lambda col: col.col_name == fk_col_name and \
                                col.table.name == fk_table_name)
        return cls.create_or_update(table, col_id,
                                    col_name = col_name,
                                    col_type = col_type,
                                    daemon_tags = daemon_tags,
                                    primary_key = pk,
                                    foreign_key = fk)
    @classmethod
    def create_column(cls, context, table, col_id, col_name, col_type, user_tags, pk, fk_info):
        if fk_info is None:
            fk = None
        else:
            fk_table_id, fk_col_id = fk_info
            fk = context.columns.get(
                    lambda col: col.col_id == fk_col_id and \
                                col.table.id == fk_table_id)
        return cls.create_or_update(table, col_id,
                                    col_name = col_name,
                                    col_type = col_type,
                                    user_tags = user_tags,
                                    primary_key = pk,
                                    foreign_key = fk)
