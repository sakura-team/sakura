import psycopg2
DB_CONN = psycopg2.connect("dbname='undertracks' user='metahuser' host='localhost' password='lmdpplbut'")


def get_types():
    cur_str = DB_CONN.cursor()
    cur_int = DB_CONN.cursor()
    cur_flo = DB_CONN.cursor()
    cur_str.execute("""select NULL::text""")
    cur_int.execute("""select NULL::int""")
    cur_flo.execute("""select NULL::float""")
    
    return {cur_str.description[0][1]: 'str',
            cur_int.description[0][1]: 'int',
            cur_flo.description[0][1]: 'float' }


OIDs = get_types()
