from itertools import count
from enum import Enum
import numpy as np
from sakura.common.errors import APIObjectDeniedError
from sakura.hub.context import get_context

# Note we want enums to count from 0, since they will serve as array indexes below
ACCESS_SCOPES = Enum('ACCESS_SCOPES', zip('public restricted private'.split(), count()))
USER_TYPES = Enum('USER_TYPES', zip('anonymous other user_ro user_rw owner'.split(), count()))
GRANT_LEVELS = Enum('GRANT_LEVELS', zip('hide list read write own'.split(), count()))

ACCESS_TABLE = [
# ACCESS_SCOPES:   public    | restricted | private    # USER_TYPES (column below)
                  'list',     'list',      'hide',     # anonymous
                  'read',     'list',      'hide',     # other
                  'read',     'read',      'read',     # user_ro
                  'write',    'write',     'write',    # user_rw
                  'own',      'own',       'own'       # owner
]
# re-format
ACCESS_TABLE = np.array(list(map(
                            lambda x: getattr(GRANT_LEVELS, x),
                            ACCESS_TABLE))
               ).reshape(len(USER_TYPES),len(ACCESS_SCOPES))

def get_user_type(obj, user):
    if user == None:
        return USER_TYPES.anonymous
    if user == obj.owner:
        return USER_TYPES.owner
    if user in obj.users_rw:
        return USER_TYPES.user_rw
    if user in obj.users_ro:
        return USER_TYPES.user_ro
    return USER_TYPES.other

def get_grant_level_generic(obj):
    user = get_context().session.user
    user_type = get_user_type(obj, user)
    access_scope = ACCESS_SCOPES(obj.access_scope)
    grant_level = ACCESS_TABLE[user_type.value, access_scope.value]
    return grant_level

class FilteredView:
    def __init__(self, db_set):
        self.db_set = db_set
    @staticmethod
    def list_access_checker(o):
        if o.get_grant_level().value < GRANT_LEVELS.list.value:
            user = get_context().session.user
            raise APIObjectDeniedError('%s is not allowed to view this item.' % \
                    ('An anonymous user' if user is None else 'User ' + user.login))
    def pack(self):
        return tuple(o.pack() for o in \
                filter(self.is_accessible, self.db_set.select()))
    def is_accessible(self, o):
        try:
            FilteredView.list_access_checker(o)
        except APIObjectDeniedError:
            return False
        return True
    def __getitem__(self, idx):
        res = self.db_set[idx]
        FilteredView.list_access_checker(res)
        return res
    def __getattr__(self, attr):
        return getattr(self.db_set, attr)
