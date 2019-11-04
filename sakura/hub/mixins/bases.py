from sakura.common.errors import APIObjectDeniedError, APIRequestError
from sakura.common.access import GRANT_LEVELS, ACCESS_TABLE
from sakura.common.tools import StatusMixin
from sakura.common.events import EventSourceMixin
from sakura.hub.access import parse_gui_access_info, find_owner, FilteredView, get_user_type
from sakura.hub.context import get_context
from sakura.hub.sendmail import sendmail

GRANT_REQUEST_MAIL_SUBJECT = "Sakura user grant request."
GRANT_REQUEST_MAIL_CONTENT = '''
Dear {owner.first_name} {owner.last_name},

Sakura user {requester.login} ({requester.first_name} {requester.last_name}, {requester.email}) is requesting \
*{grant_name}* grant to *{obj_desc}*.

He or she provided the following explanatory text:
---------------------
{req_text}
---------------------

Thanks.
Sakura platform team.
'''

GRANT_ACCEPTED_MAIL_SUBJECT = "Your sakura grant request was accepted."
GRANT_ACCEPTED_MAIL_CONTENT = '''
Dear {requester.first_name} {requester.last_name},

Sakura user {owner.login} ({owner.first_name} {owner.last_name}, {owner.email}) just accepted
your request for a *{grant_name}* grant to *{obj_desc}*.

Thanks.
Sakura platform team.
'''

GRANT_DENIED_MAIL_SUBJECT = "Your sakura grant request was DENIED."
GRANT_DENIED_MAIL_CONTENT = '''
Dear {requester.first_name} {requester.last_name},

Sakura user {owner.login} ({owner.first_name} {owner.last_name}, {owner.email}) denied
your request for a *{grant_name}* grant to *{obj_desc}*.

Sorry.
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
            if login in self.grants:
                # drop the grant
                del self.grants[login]
        elif grant_level not in (GRANT_LEVELS.own, GRANT_LEVELS.read, GRANT_LEVELS.write):
            raise APIRequestError("Only 'read' and 'write' grant levels can be set.")
        else:
            # check if a grant request was requested by this user
            if login in self.grants and 'requested_level' in self.grants[login] and \
                    self.grants[login]['requested_level'] == grant_level:
                requester = get_context().users[login]
                owner = get_context().user  # current user
                content = GRANT_ACCEPTED_MAIL_CONTENT.format(
                        owner = owner,
                        requester = requester,
                        obj_desc = self.describe(),
                        grant_name = grant_name
                )
                sendmail(requester.email, GRANT_ACCEPTED_MAIL_SUBJECT, content)
            # update
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
        content = GRANT_REQUEST_MAIL_CONTENT.format(
                owner = owner,
                requester = requester,
                obj_desc = self.describe(),
                grant_name = grant_name,
                req_text = req_text
        )
        sendmail(owner.email, GRANT_REQUEST_MAIL_SUBJECT, content)
    def deny_grant_request(self, login):
        self.assert_grant_level(GRANT_LEVELS.own,
                        'Only owner can deny grant requests.')
        if login not in self.grants or 'requested_level' not in self.grants[login]:
            raise APIRequestError('No such grant request.')
        requested_level = self.grants[login]['requested_level']
        del self.grants[login]['requested_level']
        requester = get_context().users[login]
        owner = get_context().user  # current user
        content = GRANT_DENIED_MAIL_CONTENT.format(
                owner = owner,
                requester = requester,
                obj_desc = self.describe(),
                grant_name = GRANT_LEVELS.name(requested_level)
        )
        sendmail(requester.email, GRANT_DENIED_MAIL_SUBJECT, content)
        if len(self.grants[login]) == 0:
            del self.grants[login]
        self.commit()
    def commit(self):
        get_context().db.commit()
    @classmethod
    def filter_for_current_user(cls):
        return FilteredView(cls)
