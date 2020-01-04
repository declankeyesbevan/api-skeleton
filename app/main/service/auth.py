from app.main.model.user import User
from app.main.service.blacklist import blacklist_token


# FIXME: refactor all of these, they are very hard to read
class Auth:

    @classmethod
    def login_user(cls, data):
        try:
            user = User.query.filter_by(email=data.get('email')).first()
            if user and user.check_password(data.get('password')):
                auth_token = user.encode_auth_token(user.id)
                if auth_token:
                    response_object = dict(
                        status='success',
                        message='Successfully logged in.',
                        Authorization=auth_token.decode(),
                    )
                    return response_object, 200

            response_object = dict(status='fail', message='Email or password does not match.')
            return response_object, 401
        except Exception:
            response_object = dict(status='fail', message='Try again.')
            return response_object, 500

    @classmethod
    def logout_user(cls, data):
        auth_token = data.split(' ')[1] if data else ''

        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                return blacklist_token(token=auth_token)
            response_object = dict(status='fail', message=resp)
            return response_object, 401

        response_object = dict(status='fail', message='Provide a valid auth token.')
        return response_object, 403
