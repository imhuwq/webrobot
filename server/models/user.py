import re
from random import SystemRandom
from string import ascii_letters, digits

from sqlalchemy import Column, String
from bcrypt import hashpw, checkpw, gensalt

from server.application.sqlalchemy_db import User as UserBase


class UnreadableAttr(BaseException):
    def __init__(self, *args, **kwargs):
        super(UnreadableAttr, self).__init__(*args, **kwargs)


class User(UserBase):
    name = Column('name', String, unique=True)
    email = Column('email', String, unique=True)
    __password = Column('password', String)
    auth_token = Column('auth_token', String)

    def set_password(self, value):
        if not isinstance(value, bytes):
            value = value.encode()
        self.__password = hashpw(value, gensalt())

    def authenticate(self, password):
        if not isinstance(password, bytes):
            password = password.encode()
        return checkpw(password, self.__password)

    @classmethod
    def validate_name(cls, name):

        chars = ascii_letters + digits + '._'
        chars_length = 0

        for text in name:
            if '\u4e00' <= text <= '\u9fff':
                chars_length += 2
            elif text in chars:
                chars_length += 1
            else:
                return False
        if chars_length <= 2 or chars_length >= 21:
            return False

        return True

    @classmethod
    def validate_email(cls, email):
        email_pattern = re.compile(r'[^@]+@[^@]+\.[^@]+$')
        return email_pattern.match(email) is not None

    @classmethod
    def gen_random_password(cls):
        chars = ascii_letters + digits
        codes = [SystemRandom().choice(chars) for _ in range(10)]
        password = ''.join(codes)
        return password

    def gen_auth_token(self):
        chars = ascii_letters + digits
        codes = [SystemRandom().choice(chars) for _ in range(24)]
        token = ''.join(codes)
        self.auth_token = token
        return token

    @classmethod
    def validate_password(cls, password):
        if len(password) < 7:
            return False

        letter_pattern = re.compile(r'([a-zA-Z])')
        if not letter_pattern.findall(password):
            return False

        digit_pattern = re.compile(r'(\d)')
        if not digit_pattern.findall(password):
            return False

        return True
