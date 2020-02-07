# pylint: disable=try-except-raise

from werkzeug.exceptions import BadRequest, InternalServerError, Unauthorized

from app.main.model.user import User
from app.main.service.blacklist import blacklist_token
from app.responses import EMAIL_PASSWORD, MALFORMED, OK, responder
from app.utils import SECOND


class Auth:

    @classmethod
    def login_user(cls, data):
        user = User().find_user(dict(email=data.get('email')))

        if not user or not user.check_password(data.get('password')):
            raise Unauthorized(EMAIL_PASSWORD)

        try:
            auth_token = user.encode_auth_token(user.id)
            token = auth_token.decode()
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
            User.decode_auth_token(auth_token)
        except Unauthorized:
            raise
        else:
            return blacklist_token(token=auth_token)
