import datetime
import uuid

from app.main.model.user import User
from app.main.util.dao import save_changes
from app.responses import (
    CONFLICT_PAYLOAD, CREATED, REGISTRATION_SUCCESS, SUCCESS, UNKNOWN_ERROR_PAYLOAD,
)


def save_new_user(data):
    user = User.query.filter_by(email=data['email']).first()
    if user:
        return CONFLICT_PAYLOAD

    new_user = User(
        public_id=str(uuid.uuid4()),
        email=data.get('email'),
        username=data.get('username'),
        password=data.get('password'),
        registered_on=datetime.datetime.utcnow()
    )
    save_changes(new_user)
    return generate_token(new_user)


def get_all_users():
    return User.query.all()


def get_a_user(public_id):
    return User.query.filter_by(public_id=public_id).first()


def generate_token(user):
    try:
        auth_token = user.encode_auth_token(user.id)
        response_object = dict(
            status=SUCCESS,
            message=REGISTRATION_SUCCESS,
            public_id=user.public_id,
            Authorization=auth_token.decode(),
        )
    except Exception:
        return UNKNOWN_ERROR_PAYLOAD
    else:
        return response_object, CREATED
