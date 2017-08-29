from collections import defaultdict

class Dataset:
    def __init__(self, dbms, dbname):
        self.dbms = dbms
        self.dbname = dbname
        self.owner = None
        self.users = defaultdict(lambda: dict(READ=False, WRITE=False))
    def grant(self, user, privtype):
        if privtype == 'OWNER':
            self.owner = user
        else:
            self.users[user][privtype] = True
