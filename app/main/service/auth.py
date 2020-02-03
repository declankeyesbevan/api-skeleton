from werkzeug.exceptions import BadRequest, InternalServerError, Unauthorized

from app.main.model.user import User
from app.main.service.blacklist import blacklist_token
from app.responses import (
    EMAIL_PASSWORD_PAYLOAD, MALFORMED_PAYLOAD, OK, SUCCESS,
)
from app.utils import SECOND


class Auth:

    @classmethod
    def login_user(cls, data):
        user = User().find_user_by_email(data)

        if not user:
            return EMAIL_PASSWORD_PAYLOAD

        if not user.check_password(data.get('password')):
            return EMAIL_PASSWORD_PAYLOAD

        try:
            auth_token = user.encode_auth_token(user.id)
            token = auth_token.decode()
        except InternalServerError:
            raise
        else:
            return dict(status=SUCCESS, data=dict(token=token)), OK

    @classmethod
    def logout_user(cls, data):
        try:
            auth_token = data.split('Bearer ')[SECOND]
        except (AttributeError, IndexError):
            raise BadRequest(MALFORMED_PAYLOAD)

        try:
            User.decode_auth_token(auth_token)
        except Unauthorized:
            raise
        else:
            return blacklist_token(token=auth_token)
