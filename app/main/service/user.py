import datetime
import uuid

from app.http_codes import CONFLICT, CREATED, UNAUTHORIZED
from app.main import db
from app.main.model.user import User


def save_new_user(data):
    user = User.query.filter_by(email=data['email']).first()
    if not user:
        new_user = User(
            public_id=str(uuid.uuid4()),
            email=data['email'],
            username=data['username'],
            password=data['password'],
            registered_on=datetime.datetime.utcnow()
        )
        save_changes(new_user)
        return generate_token(new_user)

    response_object = dict(status='fail', message='User already exists. Please Log in.')
    return response_object, CONFLICT


def get_all_users():
    return User.query.all()


def get_a_user(public_id):
    return User.query.filter_by(public_id=public_id).first()


def generate_token(user):
    try:
        auth_token = user.encode_auth_token(user.id)
        response_object = dict(
            status='success',
            message='Successfully registered.',
            public_id=user.public_id,
            Authorization=auth_token.decode(),
        )
    except Exception:
        response_object = dict(status='fail', message='An error occurred. Please try again.')
        return response_object, UNAUTHORIZED
    else:
        return response_object, CREATED


def save_changes(data):
    db.session.add(data)
    db.session.commit()
