class UserMixin:
    @classmethod
    def from_logins(cls, logins):
        return [cls.get(login = login) for login in logins]
    @classmethod
    def new_user(cls, context, login, email, **user_info):
        if cls.get(login = login) is not None:
            raise ValueError('login name "%s" already exists!' % login)
        if cls.get(email = email) is not None:
            raise ValueError('email "%s" already exists!' % email)
        cls(login = login, email = email, **user_info)
        context.db.commit()
    @classmethod
    def from_credentials(cls, email, password):
        user = cls.get(email = email)
        if user is None:
            raise ValueError('Email "%s" is unknown.' % email)
        if user.password != password:
            raise ValueError('Invalid password.')
        return user
