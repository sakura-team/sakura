class UserMixin:
    @classmethod
    def from_logins(cls, logins):
        return [cls.get(login = login) for login in logins]
