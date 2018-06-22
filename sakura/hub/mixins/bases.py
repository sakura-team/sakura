from sakura.common.errors import APIObjectDeniedError, APIRequestError
from sakura.common.access import GRANT_LEVELS, ACCESS_TABLE
from sakura.hub.access import parse_gui_access_info, find_owner, FilteredView, get_user_type
from sakura.hub.context import get_context
from sakura.hub.myemail import sendmail

GRANT_REQUEST_MAIL_SUBJECT = "Sakura user grant request."
GRANT_REQUEST_MAIL_CONTENT = '''
Dear %(owner_firstname)s %(owner_lastname)s,

Sakura user %(req_login)s (%(req_firstname)s %(req_lastname)s, %(req_email)s) is requesting \
*%(grant_name)s* grant to *%(obj_desc)s*.

He or she provided the following explanatory text:
---------------------
%(req_text)s
---------------------

Thanks.
Sakura platform team.
'''

class BaseMixin:
    @property
    def owner(self):
        return find_owner(self.grants)
    @owner.setter
    def owner(self, login):
        self.grants[login] = GRANT_LEVELS.own
    def cleanup_grants(self):
        users = get_context().users
        grants = dict(self.grants)
        cleaned_up_grants = {}
        for login, grant in grants.items():
            if users.get(login = login) is None:
                print('WARNING: user %s is unknown is Sakura. Ignored.' % login)
            else:
                cleaned_up_grants[login] = grant
        self.grants = cleaned_up_grants
    def parse_and_update_attributes(self, **kwargs):
        self.assert_grant_level(GRANT_LEVELS.own,
                        'Only owner can change attributes.')
        kwargs = parse_gui_access_info(**kwargs)
        self.update_attributes(**kwargs)
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
    def handle_grant_request(self, grant_name, req_text):
        requested_grant = GRANT_LEVELS.value(grant_name)
        requester_grant = self.get_grant_level()
        context = get_context()
        if not context.user_is_logged_in():
            raise APIRequestError('Please log in first!')
        if requester_grant >= requested_grant:
            raise APIRequestError('This grant level is already allowed to you!')
        if requested_grant not in (GRANT_LEVELS.read, GRANT_LEVELS.write):
            raise APIRequestError("Denied, you can only request 'read' or 'write' grants.")
        requester = context.session.user
        owner = context.users.from_login_or_email(self.owner)
        content = GRANT_REQUEST_MAIL_CONTENT % dict(
                owner_firstname = owner.first_name,
                owner_lastname = owner.last_name,
                req_login = requester.login,
                req_firstname = requester.first_name,
                req_lastname = requester.last_name,
                req_email = requester.email,
                obj_desc = self.describe(),
                grant_name = grant_name,
                req_text = req_text
        )
        sendmail(owner.email, GRANT_REQUEST_MAIL_SUBJECT, content)
    def commit(self):
        self._database_.commit()
    @classmethod
    def filter_for_web_user(cls):
        return FilteredView(cls)
