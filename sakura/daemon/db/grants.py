def as_sakura_user(db_user):
    if db_user.startswith('sakura_'):
        return db_user[7:]

def register_grant(registry, db_user, grant):
    user = as_sakura_user(db_user)
    # user is not a sakura user
    if user is None:
        return
    # a greater grant is already recorded
    if user in registry and \
            registry[user] >= grant:
        return
    # ok, let's record it
    registry[user] = grant
