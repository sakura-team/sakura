from sakura.common.errors import APIObjectDeniedError
from sakura.common.access import ACCESS_SCOPES, GRANT_LEVELS, USER_TYPES
from sakura.hub.context import get_context

GRANT_TO_USER_TYPE = {
    GRANT_LEVELS.own:   USER_TYPES.owner,
    GRANT_LEVELS.write: USER_TYPES.user_rw,
    GRANT_LEVELS.read:  USER_TYPES.user_ro
}

def get_user_type(obj, user):
    if user == None:
        return USER_TYPES.anonymous
    if user.login not in obj.grants:
        return USER_TYPES.other
    grant = obj.grants[user.login]
    return GRANT_TO_USER_TYPE[grant]

class FilteredView:
    def __init__(self, db_set):
        self.db_set = db_set
    @staticmethod
    def list_access_checker(o):
        if o.get_grant_level() < GRANT_LEVELS.list:
            user = get_context().user
            raise APIObjectDeniedError('%s is not allowed to view this item.' % \
                    ('An anonymous user' if user is None else 'User ' + user.login))
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
        res = self.db_set[idx]
        FilteredView.list_access_checker(res)
        return res
    def __getattr__(self, attr):
        return getattr(self.db_set, attr)

def parse_gui_access_info(grants = None, access_scope = None, **kwargs):
    if grants != None:
        parsed_grants = {}
        for login, grant_name in grants.items():
            parsed_grants[login] = GRANT_LEVELS.value(grant_name)
        kwargs.update(grants = parsed_grants)
    if access_scope != None:
        kwargs.update(access_scope = ACCESS_SCOPES.value(access_scope))
    return kwargs

def pack_gui_access_info(obj):
    gui_grants = {}
    owner = None
    for login, grant in obj.grants.items():
        gui_grants[login] = GRANT_LEVELS.name(grant)
        if grant == GRANT_LEVELS.own:
            owner = login
    return dict(
        owner = owner,
        grants = gui_grants,
        access_scope = ACCESS_SCOPES.name(obj.access_scope),
        grant_level = GRANT_LEVELS.name(obj.get_grant_level())
    )

def find_owner(grants):
    for login, grant in grants.items():
        if grant == GRANT_LEVELS.own:
            return login
