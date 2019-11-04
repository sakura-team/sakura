from sakura.hub.context import get_context
from sakura.hub.sendmail import sendmail
from sakura.common.errors import APIFeatureDeniedError

PRIVILEGE_REQUEST_MAIL_SUBJECT = "Sakura user privilege request."
PRIVILEGE_REQUEST_MAIL_CONTENT = '''
Dear {admin.first_name} {admin.last_name},

Sakura user {requester.login} ({requester.first_name} {requester.last_name}, {requester.email}) is requesting \
*{privilege_name}* privilege.

You can accept or deny this request at your convenience.
Note that all sakura users with 'admin' privilege will receive this email, thus it may have \
been processed already when you check it.

Thanks.
Sakura platform team.
'''

PRIVILEGE_REQUEST_ANSWER_MAIL_SUBJECT = "Your sakura user privilege request was {status}."
PRIVILEGE_REQUEST_ANSWER_MAIL_CONTENT = '''
Dear {requester.first_name} {requester.last_name},

Sakura admin user {admin.login} ({admin.first_name} {admin.last_name}, {admin.email}) {action}
your request for a *{privilege_name}* privilege.

{polite_word}.
Sakura platform team.
'''

def check_privilege(privilege):
    user = get_context().user
    if user.is_anonymous():
        return False
    return privilege in user.privileges

def assert_privilege(privilege, err_message):
    if not check_privilege(privilege):
        raise APIFeatureDeniedError(err_message)

def send_privilege_request_mail(requester, privilege):
    for admin_user in get_context().users.get_admins():
        content = PRIVILEGE_REQUEST_MAIL_CONTENT.format(
                admin = admin_user,
                requester = requester,
                privilege_name = privilege
        )
        sendmail(admin_user.email, PRIVILEGE_REQUEST_MAIL_SUBJECT, content)

def send_privilege_request_answer_mail(requester, admin, privilege, accepted):
    info = dict(
        admin = admin,
        requester = requester,
        privilege_name = privilege)
    if accepted:
        info.update(
            status = 'accepted',
            action = 'accepted',
            polite_word = 'Thanks'
        )
    else:
        info.update(
            status = 'DENIED',
            action = 'denied',
            polite_word = 'Sorry'
        )
    sendmail(requester.email,
             PRIVILEGE_REQUEST_ANSWER_MAIL_SUBJECT.format(**info),
             PRIVILEGE_REQUEST_ANSWER_MAIL_CONTENT.format(**info)
    )

