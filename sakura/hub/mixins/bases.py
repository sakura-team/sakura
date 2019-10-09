from sakura.common.errors import APIObjectDeniedError, APIRequestError
from sakura.common.access import GRANT_LEVELS, ACCESS_TABLE
from sakura.common.tools import StatusMixin
from sakura.common.events import EventSourceMixin
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

class BaseMixin(StatusMixin, EventSourceMixin):
    @property
    def owner(self):
        return find_owner(self.grants)
    @owner.setter
    def owner(self, login):
        self.update_grant(login, 'own')
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
        user_type = get_user_type(self, get_context().user)
        grant_level = ACCESS_TABLE[user_type, self.access_scope]
        return grant_level
    def assert_grant_level(self, grant, error_msg):
        if self.get_grant_level() < grant:
            raise APIObjectDeniedError(error_msg)
    def update_grant(self, login, grant_name):
        # note: an object being constructed may not have an
        # owner set yet.
        if self.owner is not None:
            self.assert_grant_level(GRANT_LEVELS.own,
                        'Only owner can change grants.')
        grant_level = GRANT_LEVELS.value(grant_name)
        if grant_level == GRANT_LEVELS.hide:
            # drop the grant
            del self.grants[login]
        elif grant_level not in (GRANT_LEVELS.own, GRANT_LEVELS.read, GRANT_LEVELS.write):
            raise APIRequestError("Only 'read' and 'write' grant levels can be set.")
        else:
            # note: if a grant request was requested by this user,
            # this update will cause the request to be cleared.
            self.grants[login] = dict(
                level = grant_level
            )
        self.commit()
    def record_grant_request(self, login, level):
        grant = self.grants.get(login, {})
        grant.update(
            requested_level = level
        )
        self.grants[login] = grant
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
        requester = context.user
        self.record_grant_request(requester.login, requested_grant)
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
        get_context().db.commit()
    @classmethod
    def filter_for_current_user(cls):
        return FilteredView(cls)
