# pylint: disable=try-except-raise

import logging
from datetime import datetime
from functools import wraps

from flask import current_app, request
from flask._compat import text_type as _
from flask_jwt_simple import create_jwt, decode_jwt, get_jwt
from flask_jwt_simple.exceptions import FlaskJWTException
from itsdangerous import BadData, URLSafeTimedSerializer
from jwt import DecodeError, ExpiredSignatureError
from werkzeug.exceptions import BadRequest, Conflict, InternalServerError, Unauthorized

from app.email_client import send_password_reset_email
from app.i18n.base import (
    ACCOUNT_ALREADY_CONFIRMED, CHECK_EMAIL, CONFIRMATION_FAILED, EMAIL_INVALID, EMAIL_NOT_CONFIRMED,
    EMAIL_NOT_CONFIRMED_RESET, EMAIL_PASSWORD, ENCODING_JWT, JWT_BLACKLISTED, JWT_EXPIRED,
    JWT_INVALID, MALFORMED, PASSWORD_UPDATED, PASSWORD_UPDATE_FAILED, RESET_FAILED,
)
from app.main.data.dao import save_changes
from app.main.model.blacklist import BlacklistToken
from app.main.model.user import User
from app.main.service.blacklist import blacklist_token
from app.main.service.user import _lookup_user_by_id
from app.responses import OK, responder
from app.security import PasswordValidator
from app.utils import SECOND

MAX_TOKEN_AGE = 600

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
            raise InternalServerError(ENCODING_JWT)
        else:
            return token

    @classmethod
    def decode_auth_token(cls, auth_token):
        try:
            payload = decode_jwt(auth_token)
        except ExpiredSignatureError:
            raise Unauthorized(JWT_EXPIRED)
        except DecodeError:
            raise Unauthorized(JWT_INVALID)
        else:
            return payload['sub']

    @classmethod
    def confirm_email(cls, token):
        user = cls.timed_serialiser(
            token, current_app.config['EMAIL_CONFIRMATION_SALT'], _(CONFIRMATION_FAILED)
        )

        if user.email_confirmed:
            raise Conflict(ACCOUNT_ALREADY_CONFIRMED)

        user.email_confirmed = True
        user.email_confirmed_on = datetime.utcnow()
        save_changes(user)

        logger.info(f"Confirmed email of user with public_id: {user.public_id}")
        return responder(code=OK)

    @classmethod
    def request_password_reset(cls, data):
        user = User().find_user(dict(email=data.get('email')))

        if not user:
            raise Unauthorized(EMAIL_INVALID)

        if not user.email_confirmed:
            raise Unauthorized(EMAIL_NOT_CONFIRMED_RESET)

        send_password_reset_email(user.email)

        logger.info(f"Password reset request of user with public_id: {user.public_id}")
        return responder(code=OK, data=dict(check=_(CHECK_EMAIL)))

    @classmethod
    def change_password(cls, data):
        user = _lookup_user_by_id(get_jwt().get('sub'))
        return cls._update_password(data, user)

    @classmethod
    def reset_password(cls, token, data):
        user = cls.timed_serialiser(
            token, current_app.config['PASSWORD_RESET_SALT'], _(RESET_FAILED)
        )
        if not user:
            raise Unauthorized(PASSWORD_UPDATE_FAILED)
        return cls._update_password(data, user)

    @classmethod
    def _update_password(cls, data, user):
        password_invalid = PasswordValidator().validate_password(data.get('password'))
        if password_invalid:
            raise BadRequest(password_invalid)
        user.password = data.get('password')
        save_changes(user)

        logger.info(f"Updating password of user with public_id: {user.public_id}")
        return responder(code=OK, data=dict(updated=_(PASSWORD_UPDATED)))

    @classmethod
    def timed_serialiser(cls, token, salt, error_message):
        try:
            serialiser = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            email = serialiser.loads(token, salt=salt, max_age=MAX_TOKEN_AGE)
        except BadData as err:
            logger.error(f"BadData: {err}")
            raise Unauthorized(error_message)
        else:
            return User.query.filter_by(email=email).first()

    @classmethod
    def validate_token_format(cls, auth_token):
        try:
            auth_token = auth_token.split('Bearer ')[SECOND]
        except (AttributeError, IndexError):
            raise BadRequest(MALFORMED)
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
