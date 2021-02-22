# pylint: disable=invalid-name, logging-fstring-interpolation, try-except-raise
# pylint: disable=missing-function-docstring

"""
Module for performing user related operations.
"""

import datetime
import logging
import uuid

from flask import current_app
from flask._compat import text_type as _
from flask_jwt_simple import get_jwt
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import BadRequest, Conflict, InternalServerError, NotFound, Unauthorized

from app.email_client import send_confirmation_email
from app.i18n.base import (
    ACCOUNT_ALREADY_CONFIRMED, CANNOT_VIEW_OTHERS, CONFIRMATION_FAILED, EMAIL_ALREADY_EXISTS,
    EMAIL_RESENT, EMAIL_UPDATED, GETTING_USERS, USER_EXISTS, USER_NOT_FOUND,
)
from app.main.data.dao import save_changes
from app.main.model.user import User
from app.main.service.common import (
    get_user_by_email, lookup_user_by_id, serialise_users, timed_serialiser,
)
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

    create_admin = User().should_create_admin(data)

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

    logger.info("New user successfully created")
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
        raise InternalServerError(GETTING_USERS) from None
    else:
        users = serialise_users(users)
        user_is_admin, user_sub = is_admin()
        if not user_is_admin:
            user = User.query.filter_by(public_id=user_sub).first()
            users = [serialise_users([user])[FIRST]]
        return responder(code=OK, data=dict(users=users))


def get_user_by_id(public_id):
    user = lookup_user_by_id(public_id, deserialise=True)
    user_is_admin, user_sub = is_admin()
    if not user_is_admin:
        if public_id != user_sub:
            raise Unauthorized(CANNOT_VIEW_OTHERS)
    return (responder(code=OK, data=dict(user=user))) if user else None


def is_admin():
    jwt_data = get_jwt()
    return jwt_data.get('roles') == 'admin', jwt_data.get('sub')


def update_email(email):
    user = get_user_by_email(email)
    if user:
        raise Conflict(EMAIL_ALREADY_EXISTS)

    updated_user = lookup_user_by_id(get_jwt().get('sub'))

    updated_user.email = email
    updated_user.email_confirmed = False
    updated_user.email_confirmed_on = None
    updated_user.email_confirmation_sent_on = datetime.datetime.utcnow()

    save_changes(updated_user)
    send_confirmation_email(updated_user.email)

    return responder(code=OK, data=dict(updated=_(EMAIL_UPDATED)))


def confirm_email(token):
    email = timed_serialiser(
        token, current_app.config['EMAIL_CONFIRMATION_SALT'], _(CONFIRMATION_FAILED)
    )
    user = get_user_by_email(email)

    if user.email_confirmed:
        raise Conflict(ACCOUNT_ALREADY_CONFIRMED)

    user.email_confirmed = True
    user.email_confirmed_on = datetime.datetime.utcnow()
    save_changes(user)

    logger.info(f"Confirmed email of user with public_id: {user.public_id}")
    return responder(code=OK)


def resend_confirmation_email(email):
    user_to_resend = get_user_by_email(email)
    if not user_to_resend:
        raise NotFound(USER_NOT_FOUND)
    if user_to_resend.email_confirmed:
        raise Conflict(ACCOUNT_ALREADY_CONFIRMED)
    user_to_resend.email_confirmation_sent_on = datetime.datetime.utcnow()
    save_changes(user_to_resend)
    send_confirmation_email(email)
    return responder(code=OK, data=dict(resent=_(EMAIL_RESENT)))
