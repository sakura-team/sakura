from collections import defaultdict

class Dataset:
    def __init__(self, dbms, label):
        self.dbms = dbms
        self.label = label
        self.owner = None
        self.users = defaultdict(lambda: dict(READ=False, WRITE=False))
    def grant(self, user, privtype):
        if privtype == 'OWNER':
            self.owner = user
        else:
            self.users[user][privtype] = True
    def get_info_serializable(self):
        return dict(
            label = self.label,
            owner = self.owner,
            users = dict(self.users)
        )
