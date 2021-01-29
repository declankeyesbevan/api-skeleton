import datetime
import random
import uuid
from string import ascii_lowercase, ascii_uppercase, digits

from app.main.model.user import User
from app.utils import SPECIAL_CHARACTERS

USERNAME_LENGTH = 16
PASSWORD_LENGTH = 12
NUM_STANDARD_CLIENT_USERS = 1
NUM_GENERIC_USERS = 3
NUM_CLIENT_USERS = 2
TOTAL_USERS = NUM_GENERIC_USERS + NUM_CLIENT_USERS
CRAP_PASSWORD = 'TooCrap'


def user_attributes(admin=False):
    attributes = dict(
        email=random_email(),
        password=random_password(),
        username=random_text(length=USERNAME_LENGTH),
        public_id=str(uuid.uuid4()),
    )
    if admin:
        attributes['admin'] = True
    return attributes


def user_model(user_data, admin=False):
    user = User(
        email=user_data.get('email'),
        password=user_data.get('password'),
        username=user_data.get('username'),
        public_id=user_data.get('public_id'),
        registered_on=datetime.datetime.utcnow(),
    )
    if admin:
        user.admin = True
    return user


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
