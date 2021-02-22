# pylint: disable=logging-fstring-interpolation, missing-function-docstring

"""
Module for functions which are common to other services. Created to prevent circular import errors.
"""

import logging

from flask import current_app
from itsdangerous import BadData, URLSafeTimedSerializer
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import InternalServerError, Unauthorized

from app.constants import FIRST
from app.i18n.base import GETTING_USER
from app.main.model.user import User

MAX_TOKEN_AGE = 600

logger = logging.getLogger('api-skeleton')


# Auth
def timed_serialiser(token, salt, error_message):
    try:
        serialiser = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        email = serialiser.loads(token, salt=salt, max_age=MAX_TOKEN_AGE)
    except BadData as err:
        logger.error(f"BadData: {err}")
        raise Unauthorized(error_message) from None
    else:
        return email


# User
def get_user_by_email(email):
    try:
        user = User.query.filter_by(email=email).first()
    except SQLAlchemyError as err:
        logger.critical(f"SQLAlchemyError: {err}", exc_info=True)
        raise InternalServerError(GETTING_USER) from None
    else:
        return user


def lookup_user_by_id(public_id, deserialise=False):
    try:
        user = User.query.filter_by(public_id=public_id).first()
    except SQLAlchemyError as err:
        logger.critical(f"SQLAlchemyError: {err}", exc_info=True)
        raise InternalServerError(GETTING_USER) from None
    else:
        if deserialise:
            return serialise_users([user])[FIRST] if user else None
        return user


def serialise_users(users):
    return [
        dict(username=user.username, public_id=user.public_id, email=user.email) for user in users
    ]
