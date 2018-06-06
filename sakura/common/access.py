import numpy as np
from sakura.common.tools import make_enum

ACCESS_SCOPES = make_enum('open', 'public', 'restricted', 'private')
GRANT_LEVELS = make_enum('hide', 'list', 'read', 'write', 'own')
USER_TYPES = make_enum('anonymous', 'other', 'user_ro', 'user_rw', 'owner')

ACCESS_TABLE = [
# ACCESS_SCOPES:   open      | public    | restricted | private    # USER_TYPES (column below)
                  'list',     'list',     'list',      'hide',     # anonymous
                  'write',    'read',     'list',      'hide',     # other
                  'write',    'read',     'read',      'read',     # user_ro
                  'write',    'write',    'write',     'write',    # user_rw
                  'own',      'own',      'own',       'own'       # owner
]
# re-format
ACCESS_TABLE = np.array(list(map(
                            lambda x: getattr(GRANT_LEVELS, x),
                            ACCESS_TABLE))
               ).reshape(len(USER_TYPES),len(ACCESS_SCOPES))
