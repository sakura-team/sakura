#!/usr/bin/env python3
import sqlite3, sys, re

USAGE = '''\
Usage: %(prog_name)s <sqlite-db-file> > <dbd-output-file>\

The output file can be copy pasted on https://app.quickdatabasediagrams.com
To generate a svg image.
'''

if len(sys.argv) < 2:
    print(USAGE % dict(prog_name = sys.argv[0]))
    sys.exit()

con = sqlite3.connect(sys.argv[1])
for statement in con.iterdump():
    if "CREATE TABLE" in statement:
        # ignore UNIQUE constraints
        statement = re.sub('UNIQUE\(.*\)', '', statement)
        part1, rest = statement.split('(', 1)
        part2, rest = rest.rsplit(')', 1)
        table_name = part1.split()[2]
        print(table_name)
        print('-' * len(table_name))
        for column_statement in part2.split(','):
            words = column_statement.split()
            if len(words) == 0:
                continue    # removed UNIQUE constraint, probably
            col_name = words[0]
            col_type = words[1]
            col_pk, col_fk = False, None
            for i, word in enumerate(words[2:]):
                if 'PRIMARY' == word.upper():
                    col_pk = True
                elif 'REFERENCES' == word.upper():
                    col_fk = i + 3
            col_desc = col_name + ' ' + col_type
            if col_pk:
                col_desc += ' PK'
            if col_fk is not None:
                fk_desc = words[col_fk]
                fk_desc = fk_desc.replace('(', '.').strip(')')
                col_desc += ' FK >- ' + fk_desc
            print(col_desc)
        print()

