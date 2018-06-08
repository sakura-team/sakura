from sakura.common.errors import APIObjectDeniedError
from sakura.common.access import GRANT_LEVELS, ACCESS_TABLE
from sakura.hub.access import find_owner, FilteredView, get_user_type
from sakura.hub.context import get_context

class BaseMixin:
    @property
    def owner(self):
        return find_owner(self.grants)
    def update_attributes(self, **kwargs):
        metadata = dict(self.metadata)
        for attr, value in kwargs.items():
            if hasattr(self, attr):
                setattr(self, attr, value)
            else:
                metadata[attr] = value
        self.metadata = metadata
    def get_grant_level(self):
        session = get_context().session
        if session is None:
            # we are processing a request coming from a daemon,
            # return max grant
            return GRANT_LEVELS.own
        user_type = get_user_type(self, session.user)
        grant_level = ACCESS_TABLE[user_type, self.access_scope]
        return grant_level
    def assert_grant_level(self, grant, error_msg):
        if self.get_grant_level() < grant:
            raise APIObjectDeniedError(error_msg)
    def update_grant(self, login, grant_name):
        self.assert_grant_level(GRANT_LEVELS.own,
                        'Only owner can change grants.')
        grants = dict(self.grants)
        grant_level = GRANT_LEVELS.value(grant_name)
        if grant_level == GRANT_LEVELS.hide:
            if login in grants:
                del grants[login]
        else:
            grants[login] = grant_level
        self.grants = grants
        self.commit()
    def commit(self):
        self._database_.commit()
    @classmethod
    def filter_for_web_user(cls):
        return FilteredView(cls)
