# pylint: disable=invalid-name, logging-format-interpolation, try-except-raise

import datetime
import logging
import uuid

from flask._compat import text_type as _
from flask_jwt_simple import get_jwt
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import BadRequest, Conflict, InternalServerError, Unauthorized

from app.email_client import send_confirmation_email
from app.i18n.base import (
    CANNOT_VIEW_OTHERS, EMAIL_ALREADY_EXISTS, EMAIL_UPDATED, GETTING_USER, GETTING_USERS,
    USER_EXISTS,
)
from app.main.data.dao import save_changes
from app.main.model.user import User
from app.responses import CREATED, OK, responder
from app.security import PasswordValidator
from app.utils import FIRST

logger = logging.getLogger('api-skeleton')


def save_new_user(data):
    filter_params = [{filter_by: data.get(filter_by)} for filter_by in ['email', 'username']]
    user_results = [User().find_user(filter_param) for filter_param in filter_params]
    user = [user for user in user_results if user]

    if user:
        raise Conflict(USER_EXISTS)

    password_invalid = PasswordValidator().validate_password(data.get('password'))
    if password_invalid:
        raise BadRequest(password_invalid)

    create_admin = User.should_create_admin(data)

    now = datetime.datetime.utcnow()
    new_user = User(
        email=data.get('email'),
        password=data.get('password'),
        username=data.get('username'),
        public_id=str(uuid.uuid4()),
        admin=create_admin,
        registered_on=now,
        email_confirmation_sent_on=now,
        email_confirmed=False,
        email_confirmed_on=None,
    )
    save_changes(new_user)
    send_confirmation_email(new_user.email)

    logger.info(f"New user successfully created")
    logger.info(f"New user email: {new_user.email}")
    logger.info(f"New user username: {new_user.username}")
    logger.info(f"New user public_id: {new_user.public_id}")

    user = dict(public_id=new_user.public_id)
    return responder(code=CREATED, data=dict(user=user))


def get_all_users():
    try:
        users = User.query.all()
    except SQLAlchemyError as err:
        logger.critical(f"SQLAlchemyError: {err}", exc_info=True)
        raise InternalServerError(GETTING_USERS)
    else:
        users = User.deserialise_users(users)
        user_is_admin, user_sub = User.is_admin()
        if not user_is_admin:
            user = User.query.filter_by(public_id=user_sub).first()
            users = [User.deserialise_users([user])[FIRST]]
        return responder(code=OK, data=dict(users=users))


def get_a_user(public_id):
    user = _lookup_user_by_id(public_id, deserialise=True)
    user_is_admin, user_sub = User.is_admin()
    if not user_is_admin:
        if public_id != user_sub:
            raise Unauthorized(CANNOT_VIEW_OTHERS)
    return (responder(code=OK, data=dict(user=user))) if user else None


def update_email(email):
    try:
        user = User.query.filter_by(email=email).first()
    except SQLAlchemyError as err:
        logger.critical(f"SQLAlchemyError: {err}", exc_info=True)
        raise InternalServerError(GETTING_USER)
    else:
        if user:
            raise Conflict(EMAIL_ALREADY_EXISTS)

    updated_user = _lookup_user_by_id(get_jwt().get('sub'))

    updated_user.email = email
    updated_user.email_confirmed = False
    updated_user.email_confirmed_on = None
    updated_user.email_confirmation_sent_on = datetime.datetime.utcnow()

    save_changes(updated_user)
    send_confirmation_email(updated_user.email)

    return responder(code=OK, data=dict(updated=_(EMAIL_UPDATED)))


def _lookup_user_by_id(public_id, deserialise=False):
    try:
        user = User.query.filter_by(public_id=public_id).first()
    except SQLAlchemyError as err:
        logger.critical(f"SQLAlchemyError: {err}", exc_info=True)
        raise InternalServerError(GETTING_USER)
    else:
        if deserialise:
            return User.deserialise_users([user])[FIRST] if user else None
        return user
