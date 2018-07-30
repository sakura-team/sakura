import operator

COMP_OP_TO_SQL_SPECIAL = {
    (operator.eq, None): 'IS NULL',
    (operator.ne, None): 'IS NOT NULL'
}

COMP_OP_TO_SQL = {
    operator.lt: '<',
    operator.le: '<=',
    operator.eq: '=',
    operator.ne: '!=',
    operator.gt: '>',
    operator.ge: '>='
}

PRINT_SQL=False
#PRINT_SQL=True

class SQLQuery:
    def __init__(self, selected_cols, conditions):
        self.selected_cols = tuple(selected_cols)
        self.conditions = tuple(conditions)
        self.offset = 0
    def set_offset(self, offset):
        self.offset = offset
    def to_sql(self):
        select_clause = 'SELECT ' + ', '.join(
            db_column.to_sql_select_clause() for db_column in self.selected_cols
        )
        tables = set(db_column.table.name for db_column in self.selected_cols)
        tables |= set(cond[0].table.name for cond in self.conditions)
        from_clause = 'FROM "' + '", "'.join(tables) + '"'
        where_clause, offset_clause, cond_vals = '', '', ()
        if len(self.conditions) > 0:
            cond_texts, cond_vals = (), ()
            for condition in self.conditions:
                cond_info = self.condition_to_sql(condition)
                cond_texts += cond_info[0]
                cond_vals += cond_info[1]
            where_clause = 'WHERE ' + ' AND '.join(cond_texts)
        if self.offset > 0:
            offset_clause = "OFFSET " + str(self.offset)
        sql_text = ' '.join((select_clause, from_clause, where_clause, offset_clause))
        return (sql_text, cond_vals)
    def execute(self, cursor):
        sql_text, values = self.to_sql()
        if PRINT_SQL:
            print(sql_text, values)
        cursor.execute(sql_text, values)
    def condition_to_sql(self, condition):
        db_column, comp_op, value = condition
        col_name = db_column.to_sql_where_clause()
        op_sql_special = COMP_OP_TO_SQL_SPECIAL.get((comp_op, value), None)
        if op_sql_special != None:
            sql = col_name + ' ' + op_sql_special
            return (sql,), ()
        else:
            op_sql = COMP_OP_TO_SQL.get(comp_op, None)
            if op_sql is None:
                op_sql = getattr(comp_op, 'SQL_OP', None)
            assert op_sql != None, ("Don't know how to write %s as an SQL operator." % str(comp_op))
            sql = col_name + ' ' + op_sql + ' ' + db_column.value_wrapper
            return (sql,), (value,)
    def select_columns(self, *col_indexes):
        new_selected_cols = tuple(self.selected_cols[index] for index in col_indexes)
        return SQLQuery(new_selected_cols, self.conditions)
    def filter(self, col_index, comp_op, other):
        db_column = self.selected_cols[col_index]
        cond = (db_column, comp_op, other)
        new_conditions = self.conditions + (cond,)
        return SQLQuery(self.selected_cols, new_conditions)

