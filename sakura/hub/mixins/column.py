from sakura.hub.context import get_context

STANDARD_COLUMN_TAGS = (
    ("statistics", ("qualitative", "quantitative", "textual")),
    ("processing", ("sorted_asc", "sorted_desc", "unique"))
)

class ColumnMixin:
    def pack(self):
        return self.col_name, self.col_type, self.tags
    @property
    def tags(self):
        # TODO: we should not expose daemon tags here, they
        # should only be used for the processing on the daemon side.
        # on the daemon side, the abstract type (e.g. timestamp, etc.)
        # should be returned when probing, instead of native db type + tags.
        return tuple(set(self.daemon_tags) | set(self.user_tags)) # union
    def pack_for_daemon(self):
        return self.col_name, self.col_type
    @classmethod
    def generate_col_id(cls, table):
        if len(table.columns) > 0:
            return max(col.col_id for col in table.columns) +1
        else:
            return 0
    @classmethod
    def create_or_update(cls, table, col_name, **kwargs):
        column = cls.get(table = table, col_name = col_name)
        if column is None:
            col_id = cls.generate_col_id(table)
            column = cls(table = table, col_id = col_id, col_name = col_name, **kwargs)
        else:
            column.set(**kwargs)
        return column
    @classmethod
    def restore_column(cls, table, col_name, col_type):
        return cls.create_or_update(table,
                                    col_name = col_name,
                                    col_type = col_type)
    @classmethod
    def create_column(cls, table, col_name, col_type, user_tags):
        return cls.create_or_update(table,
                                    col_name = col_name,
                                    col_type = col_type,
                                    user_tags = user_tags)
