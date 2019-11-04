# -*- coding: utf-8 -*-
"""User registration or login related"""
import os, hashlib, binascii, re, base64, smtplib, random, bottle
from sakura.hub.sendmail import sendmail
from sakura.hub.context import get_context
from sakura.common.errors import APIRequestError
from sakura.hub.privileges import check_privilege, assert_privilege, \
        send_privilege_request_mail, send_privilege_request_answer_mail

RECOVERY_MAIL_SUBJECT = "Password recovery"
RECOVERY_MAIL_CONTENT = '''
Dear %(firstname)s %(lastname)s,
We have received a request for password recovery from sakura user %(login)s (you).
On Sakura login window, click on "Change Password" and enter the following:

                    login or email: %(login)s
current password or recovery token: %(rec_token)s
                      new password: <your-new-password-here>
              confirm new password: <your-new-password-here>

Note: For security reasons, the recovery token expires after %(delay)d minutes.

'''

# Fake user when not logged in
class Anonymous:
    def get_full_info(self):
        return None
    def is_anonymous(self):
        return True
    def name_it(self):
        return 'An anonymous user'

class UserMixin:
    ANONYMOUS = Anonymous()

    @classmethod
    def anonymous(cls):
        return UserMixin.ANONYMOUS

    def is_anonymous(self):
        return False

    def name_it(self):
        return 'User ' + self.login

    def pack(self):
        return dict(
            login = self.login,
            first_name = self.first_name,
            last_name = self.last_name,
            privileges = self.privileges,
            requested_privileges = self.requested_privileges)

    def is_current_user(self):
        return get_context().user is self

    def update_attributes(self, email = None, **kwargs):
        if not self.is_current_user():
            raise APIRequestError("Updating attributes of someone else is not allowed.")
        if email is not None:
            if self.email != email: # verify mail is being changed
                kwargs.update(email = email)
        UserMixin.verify_user_info(self.login, **kwargs)
        # ok, verified, let's do it
        for attr, value in kwargs.items():
            setattr(self, attr, value)

    def get_full_info(self):
        result = self.pack()
        # if user is requesting its own information,
        # or user is admin, return all details.
        if self.is_current_user() or check_privilege('admin'):
            result.update(
                email = self.email,
                creation_date = self.creation_date,
                gender = self.gender,
                country = self.country,
                institution = self.institution,
                occupation = self.occupation,
                work_domain = self.work_domain)
        return result

    def request_privilege(self, privilege):
        if not self.is_current_user():
            raise APIRequestError("Requesting privileges for someone else is not allowed.")
        if privilege not in ['admin', 'developer']:
            raise APIRequestError("No such privilege '%s'.", str(privilege))
        if privilege in self.privileges:
            raise APIRequestError('You already own this privilege!')
        if privilege in self.requested_privileges:
            raise APIRequestError('You already requested this privilege!')
        self.requested_privileges.append(privilege)
        send_privilege_request_mail(self, privilege)

    def add_privilege(self, privilege):
        assert_privilege('admin', "Only users with 'admin' privilege can add or remove privileges.")
        if privilege in self.privileges:
            raise APIRequestError("This user already has '%s' privilege." % privilege)
        self.privileges.append(privilege)
        if privilege in self.requested_privileges:
            self.requested_privileges.remove(privilege)
            send_privilege_request_answer_mail(self, get_context().user, privilege, True)

    def remove_privilege(self, privilege):
        assert_privilege('admin', "Only users with 'admin' privilege can add or remove privileges.")
        if privilege not in self.privileges:
            raise APIRequestError("This user has no such privilege.")
        self.privileges.remove(privilege)

    def deny_privilege(self, privilege):
        assert_privilege('admin', "Only users with 'admin' privilege can deny privileges.")
        if privilege not in self.requested_privileges:
            raise APIRequestError("This user has not requested such privilege.")
        self.requested_privileges.remove(privilege)
        send_privilege_request_answer_mail(self, get_context().user, privilege, False)

    @classmethod
    def get_admins(cls):
        for user in cls.select():
            if 'admin' in user.privileges:
                yield user

    @classmethod
    def from_logins(cls, logins):
        return [cls.get(login = login) for login in logins]

    @classmethod
    def hash_password(cls, password, salt = None):
        if salt == None:
            salt = os.urandom(32)
        dk = hashlib.pbkdf2_hmac('sha256', bytes(password,'utf8'), salt, 100000)
        return salt, binascii.hexlify(dk)

    @classmethod
    def verify_user_info(cls, login, email = None, first_name = None, last_name = None, creation_date = None,
                            gender = None, country = None, institution = None, occupation = None,
                            work_domain = None, **wrong_kwargs):
        if email is not None:
            if cls.get(email = email) is not None:
                raise APIRequestError('Email "%s" already exists!' % email)
        if len(wrong_kwargs) > 0:
            first_wrong_arg = list(wrong_kwargs.keys())[0]
            raise APIRequestError('Invalid user attribute "%s".' % first_wrong_arg)

    @classmethod
    def new_user(cls, login, email, password, **user_info):
        # print (type(cls))
        if login in ('current', 'create', 'list', 'privileges'):  # avoid hub api conflicts
            raise APIRequestError('Login name "%s" is not allowed!' % login)
        if cls.get(login = login) is not None:
            raise APIRequestError('Login name "%s" already exists!' % login)
        cls.verify_user_info(login, email = email, **user_info)
        # if this is the first user to register to this platform, give him the 'admin' privilege
        if len(cls.select()) == 0:
            user_info['privileges'] = ['admin']
        # all checks for existing user completed here, proceeding to new user registration
        salt, hashed_password = cls.hash_password(password)
        cls(login = login, email = email, password_salt = salt, password_hash = hashed_password, **user_info)
        get_context().db.commit()
        return True

    @classmethod
    def from_login_or_email(cls, login_or_email):
        user = None
        if re.search('@',login_or_email):
            user = cls.get(email = login_or_email)
        if user is None:
            user = cls.get(login = login_or_email)
        if user is None:
            raise APIRequestError('Login and/or email "%s" is unknown.' % login_or_email)
        return user

    @classmethod
    def from_credentials(cls, login_or_email, password, err_msg = 'Invalid password.'):
        user = cls.from_login_or_email(login_or_email)
        user.check_password(password, err_msg)
        return user

    def check_password(self, password, err_msg):
        # recalculate the hash from this password to match it agains the db entry
        salt, hashed_password = self.hash_password(password, self.password_salt)
        if self.password_hash != hashed_password:
            raise APIRequestError(err_msg)

    @classmethod
    def recover_password(cls, login_or_email):
        user = cls.from_login_or_email(login_or_email)
        secret = get_context().pw_recovery_secrets.generate_secret(user.login)
        rec_token = 'rec-' + str(secret)
        content = RECOVERY_MAIL_CONTENT % dict(
                firstname = user.first_name,
                lastname = user.last_name,
                login = user.login,
                rec_token = rec_token,
                delay = get_context().PW_RECOVERY_SECRETS_LIFETIME / 60)
        sendmail(user.email, RECOVERY_MAIL_SUBJECT, content)

    @classmethod
    def change_password(cls, login_or_email, curr_passwd_or_rec_token, new_password):
        user = None
        if curr_passwd_or_rec_token.startswith('rec-'):
            try:
                secret = int(curr_passwd_or_rec_token[4:])
            except:
                raise APIRequestError('Recovery token is invalid.')
            login = get_context().pw_recovery_secrets.get_obj(secret)
            if login is None:
                raise APIRequestError('Recovery token is invalid (possibly expired).')
            # we have a valid recovery token
            user = cls.get(login = login)
            if login_or_email not in (user.login, user.email):
                raise APIRequestError('Recovery token does not match login or email entry.')
        if user is None:
            user = cls.from_credentials(login_or_email, curr_passwd_or_rec_token)
        # all is ok, update password
        user.password_salt, user.password_hash = cls.hash_password(new_password)
