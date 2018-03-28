# -*- coding: utf-8 -*-
"""User registration or login related"""
import os, hashlib, binascii, re, base64, smtplib, random, bottle
from sakura.hub.myemail import sendmail
from sakura.hub.context import get_context
from sakura.common.errors import APIRequestError

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

class UserMixin:

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
    def new_user(cls, login, email, password, **user_info):
        # print (type(cls))
        if cls.get(login = login) is not None:
            raise APIRequestError('Login name "%s" already exists!' % login)
        if cls.get(email = email) is not None:
            raise APIRequestError('Email "%s" already exists!' % email)
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
