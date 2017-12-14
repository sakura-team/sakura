# -*- coding: utf-8 -*-
"""User registration or login related"""
import os, hashlib, binascii

class UserMixin:
   
    @classmethod
    def from_logins(cls, logins):
        return [cls.get(login = login) for login in logins]
   
    @classmethod
    def new_user(cls, context, login, email, password, **user_info):
        print("in new_user function")
        print (type(cls))
        
        
        if cls.get(login = login) is not None:
            raise ValueError('Login name "%s" already exists!' % login)
        if cls.get(email = email) is not None:
            raise ValueError('Email "%s" already exists!' % email)
        
        # all checks for existing user completed here, proceeding to new user registration
        print (login)
        print (password)
        print (type(password))
        client_hashed = password
        salt = os.urandom(32)
        dk = hashlib.pbkdf2_hmac('sha256', bytes(client_hashed,'utf8'), salt, 100000)
        server_hashed = binascii.hexlify(dk)
        print (server_hashed)
        print (type(server_hashed))
        cls(login = login, email = email, password = client_hashed, salt = salt, hash = server_hashed, **user_info)
        context.db.commit()
        return True
        
    @classmethod
    def from_credentials(cls, email, password):
        user = cls.get(email = email)
        if user is None:
            raise ValueError('Email "%s" is unknown.' % email)
        if user.password != password:
            raise ValueError('Invalid password.')
        return user
