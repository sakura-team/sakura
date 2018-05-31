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
    @classmethod
    def filter_for_web_user(cls):
        return FilteredView(cls)
