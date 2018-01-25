# -*- coding: utf-8 -*-
"""User registration or login related"""
import os, hashlib, binascii, re, base64, smtplib, random
from email.mime.text import MIMEText


class UserMixin:
   
    @classmethod
    def from_logins(cls, logins):
        return [cls.get(login = login) for login in logins]
   
    @classmethod
    def new_user(cls, context, login, email, password, **user_info):
        # print (type(cls))
        
        if cls.get(login = login) is not None:
            raise ValueError('Login name "%s" already exists!' % login)
        if cls.get(email = email) is not None:
            raise ValueError('Email "%s" already exists!' % email)
        
        # all checks for existing user completed here, proceeding to new user registration
        client_hashed = password
        salt = os.urandom(32)
        dk = hashlib.pbkdf2_hmac('sha256', bytes(client_hashed,'utf8'), salt, 100000)
        server_hashed = binascii.hexlify(dk)
        cls(login = login, email = email, password_salt = salt, password_hash = server_hashed, **user_info)
        context.db.commit()
        return True
        
    @classmethod
    def from_credentials(cls, context, loginOrEmail, password):
        user = None
        if re.search('@',loginOrEmail):
            user = cls.get(email = loginOrEmail)
        if user is None:
            user = cls.get(login = loginOrEmail)
        if user is None:
            raise ValueError('Login and/or email "%s" is unknown.' % loginOrEmail)
        client_hashed = password  # receive the client_hashed password entered in the signIn form
        db_login = user.login # receive the user login from db
        db_salt = user.password_salt # receive the salt from db
        # recalculate the hash from this password to match it agains the db entry
        dk = hashlib.pbkdf2_hmac('sha256', bytes(client_hashed,'utf8'), db_salt, 100000)
        recalculated_hash = binascii.hexlify(dk)
        ##user.password_hash = recalculated_hash # force (new passwd)
        ##context.db.commit()                    # save forcing
        db_hash = user.password_hash # receive the server_hashed passwd from db
        if db_hash != recalculated_hash:
            raise ValueError('Invalid password.')
        return db_login


    @classmethod
    def pwdRecovery(cls, context, loginOrEmail):
        user = None
        if re.search('@',loginOrEmail):
            user = cls.get(email = loginOrEmail)
        if user is None:
            user = cls.get(login = loginOrEmail)
        if user is None:
            raise ValueError('Login and/or email "%s" is unknown.' % loginOrEmail)
        tmpCanSendMail = False # temporary (and below)
        if tmpCanSendMail:
            password = ''
            for i in range(10):
                password = password + "abcdefghjkmnpqrstuvwyzABDEFGHJKMNPQRSTUVWXYZ2345689-/=.,?!:+"[int(random.random()*60)]
        else:
            password = "ttt"
        client_hashed = base64.b64encode(hashlib.sha256(bytes(password,'utf8')).digest());
        salt = os.urandom(32)
        dk = hashlib.pbkdf2_hmac('sha256', client_hashed, salt, 100000)
        server_hashed = binascii.hexlify(dk)
        user.password_salt = salt
        user.password_hash = server_hashed
        #msg = MIMEText("new password (change it):'"+password+"'")
        #msg['Subject'] = 'New passord for Sakura (change it).'
        #msg['From'] = 'Sakura-Recovery'
        #msg['To'] = user.email
        #s = smtplib.SMTP('localhost')
        #s.send_message(msg)
        #s.quit()
        context.db.commit()
        return True

    @classmethod
    def changePassword(cls, context, loginOrEmail, currentPassword, newPassword):
        user = None
        if re.search('@',loginOrEmail):
            user = cls.get(email = loginOrEmail)
        if user is None:
            user = cls.get(login = loginOrEmail)
        if user is None:
            raise ValueError('Login and/or email "%s" is unknown.' % loginOrEmail)
        client_current_hashed = currentPassword  # receive the client_current_hashed password entered in the signIn form
        db_login = user.login # receive the user login from db
        db_salt = user.password_salt # receive the salt from db
        # recalculate the hash from this password to match it agains the db entry
        dk_current = hashlib.pbkdf2_hmac('sha256', bytes(client_current_hashed,'utf8'), db_salt, 100000)
        recalculated_current_hash = binascii.hexlify(dk_current)
        db_hash = user.password_hash # receive the server_hashed passwd from db
        if db_hash != recalculated_current_hash:
            raise ValueError('Invalid password.')
        else:
            client_new_hashed = newPassword  # receive the client_new_hashed password entered in the signIn form
            dk_new = hashlib.pbkdf2_hmac('sha256', bytes(client_new_hashed,'utf8'), db_salt, 100000)
            recalculated_new_hash = binascii.hexlify(dk_new)
            user.password_hash = recalculated_new_hash 
            context.db.commit()                    
        return db_login
