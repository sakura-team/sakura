import sqlite3
from pathlib import Path

# boolean handling
sqlite3.register_adapter(bool, int)
sqlite3.register_converter("BOOLEAN", lambda v: bool(int(v)))

class SQLiteDB():

    def __init__(self, path):
        self.c = None
        parent_dir = Path(path).parent
        if not parent_dir.exists():
            parent_dir.mkdir(parents=True)
        self.c = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
        # allow name-based access to columns
        self.c.row_factory = sqlite3.Row

    def __del__(self):
        if self.c != None:
            self.c.close()

    def commit(self):
        self.c.commit()

    def execute(self, query):
        return self.c.execute(query)

    def executescript(self, script):
        return self.c.executescript(script)

    # from a dictionary of the form <col_name> -> <value>
    # we want to filter-out keys that are not column names,
    # and return ([<col_name>, ...], [<value>, ...]).
    def get_cols_and_values(self, table, dictionary):
        # retrieve fields names for this table
        table_desc = self.c.execute("PRAGMA table_info(%s)" % table)
        col_names = set([ col_desc[1] for col_desc in table_desc ])
        res = {}
        for k in dictionary:
            # filter-out keys of dictionary that are not
            # a column name
            if k not in col_names:
                continue
            # store in the result dict
            res[k] = dictionary[k]
        # we prefer a tuple ([k,...],[v,...]) instead of
        # a dictionary, because in an insert query,
        # we need a list of keys and a list of values
        # with the same ordering.
        items = res.items()
        return (list(t[0] for t in items),
                list(t[1] for t in items))

    # allow statements like:
    # db.insert("network", ip=ip, switch_ip=swip)
    def insert(self, table, **kwargs):
        # insert and return True or return False
        cols, values = self.get_cols_and_values(table, kwargs)
        cursor = self.c.cursor()
        try:
            cursor.execute("""INSERT INTO %s(%s)
                VALUES (%s);""" % (
                    table,
                    ','.join(cols),
                    ','.join(['?'] * len(values))),
                tuple(values))
            self.lastrowid = cursor.lastrowid
            return True
        except sqlite3.IntegrityError:
            return False

    # allow statements like:
    # db.update("topology", "mac", switch_mac=swmac, switch_port=swport)
    def update(self, table, primary_key_name, **kwargs):
        cols, values = self.get_cols_and_values(table, kwargs)
        values.append(kwargs[primary_key_name])
        cursor = self.c.cursor()
        cursor.execute("""
                UPDATE %s
                SET %s
                WHERE %s = ?;""" % (
                    table,
                    ','.join("%s = ?" % col for col in cols),
                    primary_key_name),
                    values)
        return cursor.rowcount

    def get_where_clause_from_constraints(self, constraints):
        if len(constraints) > 0:
            return "WHERE %s" % (' AND '.join(constraints));
        else:
            return ""

    # format a where clause with ANDs on the specified columns
    def get_where_clause_pattern(self, cols):
        constraints = [ "%s=?" % col for col in cols ]
        return self.get_where_clause_from_constraints(constraints)

    # allow statements like:
    # mem_db.select("network", ip=ip)
    def select(self, table, **kwargs):
        cols, values = self.get_cols_and_values(table, kwargs)
        where_clause = self.get_where_clause_pattern(cols)
        sql = "SELECT * FROM %s %s;" % (table, where_clause)
        return self.c.execute(sql, values).fetchall()

    # same as above but expect only one matching record
    # and return it.
    def select_unique(self, table, **kwargs):
        record_list = self.select(table, **kwargs)
        if len(record_list) == 0:
            return None
        else:
            return record_list[0]

    # allow statements like:
    # db.delete("OpClass", name='Mean', daemon_id=1)
    def delete(self, table, **kwargs):
        cols, values = self.get_cols_and_values(table, kwargs)
        where_clause = self.get_where_clause_pattern(cols)
        sql = "DELETE FROM %s %s;" % (table, where_clause)
        return self.c.execute(sql, values)

    def insert_or_update(self, table, filter_keys, **kwargs):
        num_updated = self.update(table, filter_keys, **kwargs)
        if num_updated == 0:
            self.insert(table, **kwargs)
