
class DaemonToHubAPI(object):
    def __init__(self, context):
        self.context = context
    def get_login_from_email(self, email):
        u = self.context.users.get(email=email)
        if u is None:
            return None
        return u.login
