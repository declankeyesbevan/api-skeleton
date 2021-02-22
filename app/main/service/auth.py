# pylint: disable=try-except-raise, logging-fstring-interpolation, missing-class-docstring,
# pylint: disable=missing-function-docstring

"""
Module for performing authentication related operations.
"""

import logging
from functools import wraps

from flask import current_app, request
from flask._compat import text_type as _
from flask_jwt_simple import create_jwt, decode_jwt, get_jwt
from flask_jwt_simple.exceptions import FlaskJWTException
from jwt import DecodeError, ExpiredSignatureError
from werkzeug.exceptions import BadRequest, InternalServerError, Unauthorized

from app.email_client import send_password_reset_email
from app.i18n.base import (
    CHECK_EMAIL, EMAIL_INVALID, EMAIL_NOT_CONFIRMED, EMAIL_NOT_CONFIRMED_RESET, EMAIL_PASSWORD,
    ENCODING_JWT, JWT_BLACKLISTED, JWT_EXPIRED, JWT_INVALID, MALFORMED, PASSWORD_UPDATE_FAILED,
    PASSWORD_UPDATED, RESET_FAILED,
)
from app.main.data.dao import save_changes
from app.main.model.blacklist import BlacklistToken
from app.main.model.user import User
from app.main.service.blacklist import blacklist_token
from app.main.service.common import get_user_by_email, lookup_user_by_id, timed_serialiser
from app.responses import OK, responder
from app.security import PasswordValidator
from app.utils import SECOND

logger = logging.getLogger('api-skeleton')


class Auth:

    @classmethod
    def login_user(cls, data):
        user = User().find_user(dict(email=data.get('email')))

        if not user or not user.check_password(data.get('password')):
            raise Unauthorized(EMAIL_PASSWORD)

        if not user.email_confirmed:
            raise Unauthorized(EMAIL_NOT_CONFIRMED)

        try:
            token = Auth.encode_auth_token(user)
        except InternalServerError:
            raise
        else:
            logger.info(f"Logged in user with public_id: {user.public_id}")
            return responder(code=OK, data=dict(token=token))

    @classmethod
    def logout_user(cls, auth_token):
        try:
            public_id = Auth.decode_auth_token(auth_token)
        except Unauthorized:
            raise
        else:
            logger.info(f"Logged out user with public_id: {public_id}")
            return blacklist_token(token=auth_token)

    @classmethod
    def encode_auth_token(cls, user):
        try:
            token = create_jwt(identity=user)
        except FlaskJWTException as err:
            logger.critical(f"FlaskJWTException: {err}", exc_info=True)
            raise InternalServerError(ENCODING_JWT) from None
        else:
            return token

    @classmethod
    def decode_auth_token(cls, auth_token):
        try:
            payload = decode_jwt(auth_token)
        except ExpiredSignatureError:
            raise Unauthorized(JWT_EXPIRED) from None
        except DecodeError:
            raise Unauthorized(JWT_INVALID) from None
        else:
            return payload['sub']

    @classmethod
    def request_password_reset(cls, email):
        user = User().find_user(dict(email=email))

        if not user:
            raise Unauthorized(EMAIL_INVALID)

        if not user.email_confirmed:
            raise Unauthorized(EMAIL_NOT_CONFIRMED_RESET)

        send_password_reset_email(user.email)

        logger.info(f"Password reset request of user with public_id: {user.public_id}")
        return responder(code=OK, data=dict(check=_(CHECK_EMAIL)))

    @classmethod
    def change_password(cls, password):
        user = lookup_user_by_id(get_jwt().get('sub'))
        return cls._update_password(password, user)

    @classmethod
    def reset_password(cls, token, password):
        email = timed_serialiser(
            token, current_app.config['PASSWORD_RESET_SALT'], _(RESET_FAILED)
        )
        user = get_user_by_email(email)
        if not user:
            raise Unauthorized(PASSWORD_UPDATE_FAILED)
        return cls._update_password(password, user)

    @classmethod
    def _update_password(cls, password, user):
        password_invalid = PasswordValidator().validate_password(password)
        if password_invalid:
            raise BadRequest(password_invalid)
        user.password = password
        save_changes(user)

        logger.info(f"Updating password of user with public_id: {user.public_id}")
        return responder(code=OK, data=dict(updated=_(PASSWORD_UPDATED)))

    @classmethod
    def validate_token_format(cls, auth_token):
        try:
            auth_token = auth_token.split('Bearer ')[SECOND]
        except (AttributeError, IndexError):
            raise BadRequest(MALFORMED) from None
        else:
            return auth_token

    @classmethod
    def validate_token_blacklist(cls, auth_token):
        is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
        if is_blacklisted_token:
            raise Unauthorized(JWT_BLACKLISTED)


def jwt_valid(func):
    @wraps(func)
    def token_validator(*args, **kwargs):
        auth_token = Auth.validate_token_format(request.headers.get('Authorization'))
        Auth.validate_token_blacklist(auth_token)
        return func(*args, **kwargs)

    return token_validator
