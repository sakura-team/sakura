from sakura.common.errors import APIObjectDeniedError
from sakura.common.access import GRANT_LEVELS
from sakura.hub.access import find_owner, \
           FilteredView, get_grant_level_generic

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
        return get_grant_level_generic(self)
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
