import sqlite3
from pathlib import Path

QUOTE="'"

def quoted(string):
    s = str(string)
    if s == 'NULL':
        return s
    else:
        return QUOTE + s + QUOTE

class SQLiteDB():

    def __init__(self, path):
        self.c = None
        parent_dir = Path(path).parent
        if not parent_dir.exists():
            parent_dir.mkdir(parents=True)
        self.c = sqlite3.connect(path)
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
    # format the value for usage in an SQL statement,
    # and return (<col_name>, <value>) tuples.
    def get_tuples(self, table, dictionary):
        # retrieve fields names for this table
        table_desc = self.c.execute("PRAGMA table_info(%s)" % table)
        col_names = set([ col_desc[1] for col_desc in table_desc ])

        res = {}
        for k in dictionary:
            # filter-out keys of dictionary that are not
            # a column name
            if k not in col_names:
                continue

            # format the value appropriately for an SQL
            # statement
            value = dictionary[k]
            if value == None:
                value = 'NULL'
            else:
                value = quoted(value)

            # store in the result dict
            res[k] = value
        # we prefer a list of (k,v) items instead of
        # a dictionary, because in an insert query,
        # we need a list of keys and a list of values
        # with the same ordering.
        return res.items()

    # allow statements like:
    # db.insert("network", ip=ip, switch_ip=swip)
    def insert(self, table, **kwargs):
        # insert and return True or return False
        tuples = self.get_tuples(table, kwargs)
        cursor = self.c.cursor()
        try:
            cursor.execute("""INSERT INTO %s(%s)
                VALUES (%s);""" % (
                    table,
                    ','.join(t[0] for t in tuples),
                    ','.join(t[1] for t in tuples)))
            self.lastrowid = cursor.lastrowid
            return True
        except sqlite3.IntegrityError:
            return False

    # allow statements like:
    # db.update("topology", "mac", switch_mac=swmac, switch_port=swport)
    def update(self, table, primary_key_name, **kwargs):
        tuples = self.get_tuples(table, kwargs)
        num_modified = len(self.c.execute("""
                UPDATE %s
                SET %s
                WHERE %s = %s;""" % (
                    table,
                    ','.join("%s = %s" % t for t in tuples),
                    primary_key_name,
                    quoted(kwargs[primary_key_name]))).fetchall())
        return num_modified

    # allow statements like:
    # mem_db.select("network", ip=ip)
    def select(self, table, **kwargs):
        constraints = [ "%s=%s" % t for t in \
                self.get_tuples(table, kwargs) ]
        if len(constraints) > 0:
            where_clause = "WHERE %s" % (
                ' AND '.join(constraints));
        else:
            where_clause = ""
        return self.c.execute("SELECT * FROM %s %s;" % (
                    table, where_clause)).fetchall()

    # same as above but expect only one matching record
    # and return it.
    def select_unique(self, table, **kwargs):
        record_list = self.select(table, **kwargs)
        if len(record_list) == 0:
            return None
        else:
            return record_list[0]

