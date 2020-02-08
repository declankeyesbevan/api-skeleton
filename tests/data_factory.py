import datetime
import random
from string import ascii_lowercase, ascii_uppercase, digits

from app.main.model.blacklist import BlacklistToken
from app.main.model.user import User
from app.utils import SPECIAL_CHARACTERS

USERNAME_LENGTH = 16
PASSWORD_LENGTH = 12


def user_attributes():
    return dict(
        email=random_email(),
        password=random_password(),
        username=random_text(length=USERNAME_LENGTH),
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
    return f'{random_text(length=length)}@foomail.com'


def random_text(length=8):
    s = f'{digits}{ascii_uppercase}{ascii_lowercase}'
    return ''.join(random.choice(s) for _ in range(length))


def random_password():
    required = (
        f'{random.choice(ascii_uppercase)}'
        f'{random.choice(ascii_lowercase)}'
        f'{random.choice(digits)}'
        f'{random.choice(SPECIAL_CHARACTERS)}'
    )
    rest = random_text(PASSWORD_LENGTH - len(required))
    return f'{required}{rest}'
