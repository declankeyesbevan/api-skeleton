# pylint: disable=invalid-name, logging-format-interpolation, try-except-raise

import datetime
import logging
import uuid

from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import Conflict, InternalServerError

from app.main.data.dao import save_changes
from app.main.model.user import User
from app.responses import CREATED, OK, USER_EXISTS, responder
from app.utils import FIRST

logger = logging.getLogger('api-skeleton')


def save_new_user(data):
    filter_params = [{filter_by: data.get(filter_by)} for filter_by in ['email', 'username']]
    user_results = [User().find_user(filter_param) for filter_param in filter_params]
    user = [user for user in user_results if user]

    if user:
        raise Conflict(USER_EXISTS)

    new_user = User(
        email=data.get('email'),
        password=data.get('password'),
        username=data.get('username'),
        public_id=str(uuid.uuid4()),
        registered_on=datetime.datetime.utcnow(),
    )
    save_changes(new_user)
    logger.info(f"New user successfully created")
    logger.info(f"New user email: {new_user.email}")
    logger.info(f"New user username: {new_user.username}")
    logger.info(f"New user public_id: {new_user.public_id}")
    return generate_token(new_user)


def get_all_users():
    try:
        users = User.query.all()
    except SQLAlchemyError as err:
        raise InternalServerError(f"Error getting all users: {err}")
    else:
        users = User.deserialise_users(users)
        return responder(code=OK, data=dict(users=users))


def get_a_user(public_id):
    try:
        user = User.query.filter_by(public_id=public_id).first()
    except SQLAlchemyError as err:
        raise InternalServerError(f"Error getting a user: {err}")
    else:
        user = User.deserialise_users([user])[FIRST] if user else None
        return (responder(code=OK, data=dict(user=user))) if user else None


def generate_token(user):
    try:
        auth_token = user.encode_auth_token(user.id)
    except InternalServerError:
        raise
    else:
        logger.info(f"Generated auth token for user with public_id: {user.public_id}")
        user = dict(public_id=user.public_id, token=auth_token.decode())
        return responder(code=CREATED, data=dict(user=user))
