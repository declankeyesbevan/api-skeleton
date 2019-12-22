from app.main.model.user import User
from app.main.service.blacklist_service import save_token


class Auth:

    @classmethod
    def login_user(cls, data):
        try:
            # fetch the user data
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

            response_object = dict(status='fail', message='email or password does not match.')
            return response_object, 401
        except Exception as exc:
            print(exc)
            response_object = dict(status='fail', message='Try again.')
            return response_object, 500

    @classmethod
    def logout_user(cls, data):
        if data:
            auth_token = data.split(' ')[1]
        else:
            auth_token = ''

        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                # mark the token as blacklisted
                return save_token(token=auth_token)
            response_object = dict(status='fail', message=resp)
            return response_object, 401

        response_object = dict(status='fail', message='Provide a valid auth token.')
        return response_object, 403

    @classmethod
    def get_logged_in_user(cls, new_request):
        # get the auth token
        auth_token = new_request.headers.get('Authorization')
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                user = User.query.filter_by(id=resp).first()
                response_object = dict(
                    status='success',
                    data=dict(
                        user_id=user.id,
                        email=user.email,
                        admin=user.admin,
                        registered_on=str(user.registered_on)
                    )
                )
                return response_object, 200

            response_object = dict(status='fail', message=resp)
            return response_object, 401

        response_object = dict(status='fail', message='Provide a valid auth token.')
        return response_object, 401
