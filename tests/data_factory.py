import datetime
import random

from app.main.model.blacklist import BlacklistToken
from app.main.model.user import User


def user_attributes():
    return dict(
        email=random_email(),
        password=random_text(length=16),
        username=random_text(length=8),
    )


def user_model(user_data):
    return User(
        email=user_data.get('email'),
        password=user_data.get('password'),
        registered_on=datetime.datetime.utcnow()
    )


def blacklist_token_model(user_obj):
    return BlacklistToken(
        token=user_obj.encode_auth_token(user_obj.id)
    )


def random_email(length=8):
    return f'{random_text(length=length)}@gmail.com'


def random_text(length=8):
    s = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    return ''.join(random.choice(s) for _ in range(length))
