# pylint: disable=try-except-raise

from flask_jwt_simple import create_jwt, decode_jwt
from flask_jwt_simple.exceptions import FlaskJWTException
from jwt import DecodeError, ExpiredSignatureError
from werkzeug.exceptions import BadRequest, InternalServerError, Unauthorized

from app.i18n.base import (
    EMAIL_PASSWORD, ENCODING_JWT, JWT_BLACKLISTED, JWT_EXPIRED, JWT_INVALID, MALFORMED,
)
from app.main.model.blacklist import BlacklistToken
from app.main.model.user import User
from app.main.service.blacklist import blacklist_token
from app.responses import OK, responder
from app.utils import SECOND


class Auth:

    @classmethod
    def login_user(cls, data):
        user = User().find_user(dict(email=data.get('email')))

        if not user or not user.check_password(data.get('password')):
            raise Unauthorized(EMAIL_PASSWORD)

        try:
            token = Auth.encode_auth_token(user)
        except InternalServerError:
            raise
        else:
            return responder(code=OK, data=dict(token=token))

    @classmethod
    def logout_user(cls, data):
        try:
            auth_token = data.split('Bearer ')[SECOND]
        except (AttributeError, IndexError):
            raise BadRequest(MALFORMED)

        try:
            Auth.decode_auth_token(auth_token)
        except Unauthorized:
            raise
        else:
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
