from sakura.common.errors import APIRequestError, APIObjectDeniedError
from sakura.common.access import ACCESS_SCOPES, GRANT_LEVELS, USER_TYPES
from sakura.hub.context import get_context

GRANT_TO_USER_TYPE = {
    GRANT_LEVELS.own:   USER_TYPES.owner,
    GRANT_LEVELS.write: USER_TYPES.user_rw,
    GRANT_LEVELS.read:  USER_TYPES.user_ro
}

def get_user_type(obj, user):
    if user.is_anonymous():
        return USER_TYPES.anonymous
    for login, grant in obj.grants.items():
        if user.login == login:
            level = grant.get('level', None)
            if level is not None:
                return GRANT_TO_USER_TYPE[level]
    return USER_TYPES.other

class FilteredView:
    def __init__(self, db_set):
        self.db_set = db_set
    @staticmethod
    def list_access_checker(o):
        if o.get_grant_level() < GRANT_LEVELS.list:
            user = get_context().user
            raise APIObjectDeniedError('%s is not allowed to view this item.' % user.name_it())
    def pack(self):
        return tuple(o.pack() for o in self)
    def is_accessible(self, o):
        try:
            FilteredView.list_access_checker(o)
        except APIObjectDeniedError:
            return False
        return True
    def __iter__(self):
        return filter(self.is_accessible,
                    self.db_set.select().order_by(lambda o: o.id))
    def __getitem__(self, idx):
        try:
            res = self.db_set[idx]
        except:
            raise APIRequestError('No such object')
        FilteredView.list_access_checker(res)
        return res
    def __getattr__(self, attr):
        return getattr(self.db_set, attr)

def parse_gui_access_info(access_scope = None, **kwargs):
    if access_scope != None:
        kwargs.update(access_scope = ACCESS_SCOPES.value(access_scope))
    return kwargs

def parse_daemon_grants(daemon_grants):
    users = get_context().users
    grants = {}
    for login, level in daemon_grants.items():
        user = users.get(login = login)
        if user is None:
            print('WARNING: user %s is unknown in Sakura. Ignored.' % login)
            continue
        grants[login] = dict(
            level = level
        )
    return grants

def pack_gui_grant(grant):
    gui_grant = {}
    level = grant.get('level', None)
    if level is not None:
        gui_grant['level'] = GRANT_LEVELS.name(level)
    requested_level = grant.get('requested_level', None)
    if requested_level is not None:
        gui_grant['requested_level'] = GRANT_LEVELS.name(requested_level)
    return gui_grant

def pack_gui_access_info(obj):
    gui_grants = {}
    owner = None
    for login, grant in obj.grants.items():
        gui_grants[login] = pack_gui_grant(grant)
        if grant.get('level', None) == GRANT_LEVELS.own:
            owner = login
    return dict(
        owner = owner,
        grants = gui_grants,
        access_scope = ACCESS_SCOPES.name(obj.access_scope),
        grant_level = GRANT_LEVELS.name(obj.get_grant_level())
    )

def find_owner(grants):
    for login, grant in grants.items():
        if grant.get('level', None) == GRANT_LEVELS.own:
            return login
