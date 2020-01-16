from app.exceptions import UnauthorisedException
from app.main.model.user import User
from app.main.service.blacklist import blacklist_token
from app.responses import (
    FAIL, LOGIN_SUCCESS, MALFORMED_PAYLOAD, OK, SUCCESS, UNAUTHORISED_PAYLOAD, UNAUTHORIZED,
    UNKNOWN_ERROR_PAYLOAD,
)


class Auth:

    @classmethod
    def login_user(cls, data):
        try:
            user = User.query.filter_by(email=data.get('email')).first()
        except Exception:
            return UNKNOWN_ERROR_PAYLOAD
        else:
            if not user:
                return UNAUTHORISED_PAYLOAD

        if not user.check_password(data.get('password')):
            return UNAUTHORISED_PAYLOAD

        try:
            auth_token = user.encode_auth_token(user.id)
            token = auth_token.decode()
        except Exception:
            return UNKNOWN_ERROR_PAYLOAD
        else:
            return dict(status=SUCCESS, message=LOGIN_SUCCESS, Authorization=token), OK

    @classmethod
    def logout_user(cls, data):
        try:
            auth_token = data.split('Bearer ')[1]
        except (AttributeError, IndexError):
            return MALFORMED_PAYLOAD

        try:
            User.decode_auth_token(auth_token)
        except UnauthorisedException as exc:
            return dict(status=FAIL, message=exc.args[0]), UNAUTHORIZED
        except Exception:
            return UNKNOWN_ERROR_PAYLOAD
        else:
            return blacklist_token(token=auth_token)
