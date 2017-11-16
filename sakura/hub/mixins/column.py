class ColumnMixin:
    def pack(self):
        tags = tuple(set(self.daemon_tags) | set(self.user_tags)) # union
        return self.col_name, self.col_type, tags
    @classmethod
    def create_or_update(cls, table, db_col_name, col_type, col_tags):
        column = cls.get(table = table, db_col_name = db_col_name)
        if column is None:
            column = cls(table = table, db_col_name = db_col_name,
                col_name = db_col_name, col_type = col_type, daemon_tags = col_tags)
        else:
            column.set(col_type = col_type, daemon_tags = col_tags)
        return column
    @classmethod
    def restore_column(cls, context, *args):
        return cls.create_or_update(*args)
