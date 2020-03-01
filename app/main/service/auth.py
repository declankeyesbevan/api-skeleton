# pylint: disable=try-except-raise
import logging
from datetime import datetime

from flask import current_app
from flask_jwt_simple import create_jwt, decode_jwt
from flask_jwt_simple.exceptions import FlaskJWTException
from itsdangerous import BadData, URLSafeTimedSerializer
from jwt import DecodeError, ExpiredSignatureError
from werkzeug.exceptions import BadRequest, Conflict, InternalServerError, Unauthorized

from app.i18n.base import (
    ACCOUNT_ALREADY_CONFIRMED, CONFIRMATION_FAILED, EMAIL_NOT_CONFIRMED, EMAIL_PASSWORD,
    ENCODING_JWT, JWT_BLACKLISTED, JWT_EXPIRED, JWT_INVALID, MALFORMED,
)
from app.main.data.dao import save_changes
from app.main.model.blacklist import BlacklistToken
from app.main.model.user import User
from app.main.service.blacklist import blacklist_token
from app.responses import OK, responder
from app.utils import SECOND

MAX_EMAIL_AGE = 600

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
    def logout_user(cls, data):
        try:
            auth_token = data.split('Bearer ')[SECOND]
        except (AttributeError, IndexError):
            raise BadRequest(MALFORMED)

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
            raise InternalServerError(f"{ENCODING_JWT}: {err}")
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
            is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
            if is_blacklisted_token:
                raise Unauthorized(JWT_BLACKLISTED)
            return payload['sub']

    @classmethod
    def confirm_email(cls, token):
        try:
            confirm_serialiser = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            email = confirm_serialiser.loads(
                token, salt=current_app.config['EMAIL_SALT'], max_age=MAX_EMAIL_AGE
            )
        except BadData as err:
            raise Unauthorized(f"{CONFIRMATION_FAILED}: {err}")
        else:
            user = User.query.filter_by(email=email).first()

        if user.email_confirmed:
            raise Conflict(ACCOUNT_ALREADY_CONFIRMED)

        user.email_confirmed = True
        user.email_confirmed_on = datetime.utcnow()
        save_changes(user)

        logger.info(f"Confirmed email of user with public_id: {user.public_id}")
        return responder(code=OK)
