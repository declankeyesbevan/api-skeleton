import datetime
import uuid

from app.main.data.dao import save_changes
from app.main.model.user import User
from app.responses import CONFLICT_PAYLOAD, CREATED, OK, SUCCESS, UNKNOWN_ERROR_PAYLOAD
from app.utils import FIRST


def save_new_user(data):
    user = User.query.filter_by(email=data['email']).first()
    if user:
        return CONFLICT_PAYLOAD

    new_user = User(
        email=data.get('email'),
        password=data.get('password'),
        username=data.get('username'),
        public_id=str(uuid.uuid4()),
        registered_on=datetime.datetime.utcnow(),
    )
    save_changes(new_user)
    return generate_token(new_user)


def get_all_users():
    try:
        users = User.query.all()
    except Exception:
        return UNKNOWN_ERROR_PAYLOAD
    else:
        users = User.deserialise_users(users)
        return dict(status=SUCCESS, data=dict(users=users)), OK


def get_a_user(public_id):
    try:
        user = User.query.filter_by(public_id=public_id).first()
    except Exception:
        return UNKNOWN_ERROR_PAYLOAD
    else:
        user = User.deserialise_users([user])[FIRST] if user else None
        return (dict(status=SUCCESS, data=dict(user=user)), OK) if user else None


def generate_token(user):
    try:
        auth_token = user.encode_auth_token(user.id)
        user = dict(public_id=user.public_id, token=auth_token.decode())
    except Exception:
        return UNKNOWN_ERROR_PAYLOAD
    else:
        return dict(status=SUCCESS, data=dict(user=user)), CREATED
