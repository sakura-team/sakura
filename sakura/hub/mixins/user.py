# -*- coding: utf-8 -*-
"""User registration or login related"""
import os, hashlib, binascii, re

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
    def from_credentials(cls, loginOrEmail, password):
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
        db_hash = user.password_hash # receive the server_hashed passwd from db
        # recalculate the hash from this password to match it agains the db entry
        dk = hashlib.pbkdf2_hmac('sha256', bytes(client_hashed,'utf8'), db_salt, 100000)
        recalculated_hash = binascii.hexlify(dk)
        if db_hash != recalculated_hash:
            raise ValueError('Invalid password.')
        return db_login
